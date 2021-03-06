#include <libcaer/libcaer.h>
#include <libcaer/devices/dvs128.h>
#include <signal.h>
#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h> 
#include <unistd.h> 
#include <string.h> 
#include <sys/types.h> 
#include <sys/socket.h> 
#include <arpa/inet.h> 
#include <netinet/in.h> 

#define PORT     8000 

static atomic_bool globalShutdown = ATOMIC_VAR_INIT(false);



static void usbShutdownHandler(void *ptr) {
	(void) (ptr); // UNUSED.

	atomic_store(&globalShutdown, true);
}

int main(void) 
{
	caerDeviceHandle dvs128_handle = caerDeviceOpen(1, CAER_DEVICE_DVS128, 0, 0, NULL);
	if (dvs128_handle == NULL) {return (EXIT_FAILURE);}

	caerDeviceSendDefaultConfig(dvs128_handle);
	
	// Tweak some biases, to increase bandwidth in this case.
	caerDeviceConfigSet(dvs128_handle, DVS128_CONFIG_BIAS, DVS128_CONFIG_BIAS_PR, 695);
	caerDeviceConfigSet(dvs128_handle, DVS128_CONFIG_BIAS, DVS128_CONFIG_BIAS_FOLL, 867);

	caerDeviceDataStart(dvs128_handle, NULL, NULL, NULL, &usbShutdownHandler, NULL);

	int sockfd; 
	 
	struct sockaddr_in servaddr; 
  	sockfd = socket(AF_INET, SOCK_DGRAM, 0);
	if (sockfd < 0) 
  	{ 
		perror("socket creation failed"); 
		exit(EXIT_FAILURE); 
	} 

	memset(&servaddr, 0, sizeof(servaddr)); 
	 
	servaddr.sin_family = AF_INET; 
	servaddr.sin_port = htons(PORT); 
	servaddr.sin_addr.s_addr = INADDR_ANY;
    bool flag = true;
    int32_t ts2 = 0;
    printf("Reading datas...\n");
	while (!atomic_load_explicit(&globalShutdown, memory_order_relaxed)) 
	{
		caerEventPacketContainer packetContainer = caerDeviceDataGet(dvs128_handle);
		if (packetContainer == NULL){continue;}

		for (int32_t i = 0; i < caerEventPacketContainerGetEventPacketsNumber(packetContainer); i++) 
		{
			caerEventPacketHeader packetHeader = caerEventPacketContainerGetEventPacket(packetContainer, i);
			if (packetHeader == NULL){continue;}

			// Packet 0 is always the special events packet for DVS128, while packet is the polarity events packet.
			if (i == POLARITY_EVENT) 
			{
				caerPolarityEventPacket polarity = (caerPolarityEventPacket) packetHeader;
				int8_t arrayToSend[5 * caerEventPacketHeaderGetEventNumber(packetHeader)];
				
				for(int16_t j = 0; j < caerEventPacketHeaderGetEventNumber(packetHeader); j++)
				{
					// Get full timestamp and addresses of first event.
					caerPolarityEvent firstEvent = caerPolarityEventPacketGetEvent(polarity, j);
					int8_t pol = caerPolarityEventGetPolarity(firstEvent);
					int8_t x = caerPolarityEventGetX(firstEvent);
					int8_t y = caerPolarityEventGetY(firstEvent);
					int32_t ts1 = caerPolarityEventGetTimestamp(firstEvent);
					
					if (flag == true)
					{
						ts2 = ts1;						
					    flag = false;
					}
					unsigned int ts = ts1 - ts2;
					
					unsigned char ts_LSB  = ts        & 0xff;
					unsigned char ts_MSB = (ts >> 8)  & 0xff;  					
					
					ts2 = ts1;
					
					arrayToSend[j] = pol;
					arrayToSend[j + caerEventPacketHeaderGetEventNumber(packetHeader)] = x;
					arrayToSend[j + (2 * caerEventPacketHeaderGetEventNumber(packetHeader))] = y;
					arrayToSend[j + (3 * caerEventPacketHeaderGetEventNumber(packetHeader))] = ts_LSB;
					arrayToSend[j + (4 * caerEventPacketHeaderGetEventNumber(packetHeader))] = ts_MSB;					
				}
				sendto(sockfd, arrayToSend, sizeof(arrayToSend), 0, (struct sockaddr *) &servaddr, sizeof(servaddr));
			}
		}

		caerEventPacketContainerFree(packetContainer);
	}

	caerDeviceDataStop(dvs128_handle);

	caerDeviceClose(&dvs128_handle);

	printf("Shutdown successful.\n");

	return (EXIT_SUCCESS);
}
