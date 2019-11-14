#include <libcaer/libcaer.h>
#include <libcaer/devices/edvs.h>
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

static void globalShutdownSignalHandler(int signal) {
	// Simply set the running flag to false on SIGTERM and SIGINT (CTRL+C) for global shutdown.
	if (signal == SIGTERM || signal == SIGINT) {
		atomic_store(&globalShutdown, true);
	}
}

static void serialShutdownHandler(void *ptr) {
	(void) (ptr); // UNUSED.

	atomic_store(&globalShutdown, true);
}

int main(void) {
// Install signal handler for global shutdown.
#if defined(_WIN32)
	if (signal(SIGTERM, &globalShutdownSignalHandler) == SIG_ERR) {
		caerLog(CAER_LOG_CRITICAL, "ShutdownAction", "Failed to set signal handler for SIGTERM. Error: %d.", errno);
		return (EXIT_FAILURE);
	}

	if (signal(SIGINT, &globalShutdownSignalHandler) == SIG_ERR) {
		caerLog(CAER_LOG_CRITICAL, "ShutdownAction", "Failed to set signal handler for SIGINT. Error: %d.", errno);
		return (EXIT_FAILURE);
	}
#else
	struct sigaction shutdownAction;

	shutdownAction.sa_handler = &globalShutdownSignalHandler;
	shutdownAction.sa_flags   = 0;
	sigemptyset(&shutdownAction.sa_mask);
	sigaddset(&shutdownAction.sa_mask, SIGTERM);
	sigaddset(&shutdownAction.sa_mask, SIGINT);

	if (sigaction(SIGTERM, &shutdownAction, NULL) == -1) {
		caerLog(CAER_LOG_CRITICAL, "ShutdownAction", "Failed to set signal handler for SIGTERM. Error: %d.", errno);
		return (EXIT_FAILURE);
	}

	if (sigaction(SIGINT, &shutdownAction, NULL) == -1) {
		caerLog(CAER_LOG_CRITICAL, "ShutdownAction", "Failed to set signal handler for SIGINT. Error: %d.", errno);
		return (EXIT_FAILURE);
	}
#endif

	// Open an EDVS-4337, give it a device ID of 1, on the default Linux USB serial port.
	caerDeviceHandle edvs_handle
		= caerDeviceOpenSerial(1, CAER_DEVICE_EDVS, "/dev/ttyUSB0", CAER_HOST_CONFIG_SERIAL_BAUD_RATE_4M);
	if (edvs_handle == NULL) {
		return (EXIT_FAILURE);
	}

	// Let's take a look at the information we have on the device.
	struct caer_edvs_info edvs_info = caerEDVSInfoGet(edvs_handle);

	printf("%s --- ID: %d, Master: %d, DVS X: %d, DVS Y: %d.\n", edvs_info.deviceString, edvs_info.deviceID,
		edvs_info.deviceIsMaster, edvs_info.dvsSizeX, edvs_info.dvsSizeY);

	// Send the default configuration before using the device.
	// No configuration is sent automatically!
	caerDeviceSendDefaultConfig(edvs_handle);

	// Tweak some biases, to increase bandwidth in this case.
	caerDeviceConfigSet(edvs_handle, EDVS_CONFIG_BIAS, EDVS_CONFIG_BIAS_PR, 695);
	caerDeviceConfigSet(edvs_handle, EDVS_CONFIG_BIAS, EDVS_CONFIG_BIAS_FOLL, 867);

	// Let's verify they really changed!
	uint32_t prBias, follBias;
	caerDeviceConfigGet(edvs_handle, EDVS_CONFIG_BIAS, EDVS_CONFIG_BIAS_PR, &prBias);
	caerDeviceConfigGet(edvs_handle, EDVS_CONFIG_BIAS, EDVS_CONFIG_BIAS_FOLL, &follBias);

	printf("New bias values --- PR: %d, FOLL: %d.\n", prBias, follBias);

	// Now let's get start getting some data from the device. We just loop in blocking mode,
	// no notification needed regarding new events. The shutdown notification, for example if
	// the device is disconnected, should be listened to.
	caerDeviceDataStart(edvs_handle, NULL, NULL, NULL, &serialShutdownHandler, NULL);

	// Let's turn on blocking data-get mode to avoid wasting resources.
	caerDeviceConfigSet(edvs_handle, CAER_HOST_CONFIG_DATAEXCHANGE, CAER_HOST_CONFIG_DATAEXCHANGE_BLOCKING, true);

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
		caerEventPacketContainer packetContainer = caerDeviceDataGet(edvs_handle);
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

	caerDeviceDataStop(edvs_handle);

	caerDeviceClose(&edvs_handle);

	printf("Shutdown successful.\n");

	return (EXIT_SUCCESS);
}
