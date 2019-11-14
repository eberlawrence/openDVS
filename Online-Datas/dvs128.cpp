#define LIBCAER_FRAMECPP_OPENCV_INSTALLED 0
#include <libcaercpp/devices/dvs128.hpp>
#include <atomic>
#include <csignal>
#include <stdlib.h> 
#include <unistd.h> 
#include <string.h> 
#include <sys/types.h> 
#include <sys/socket.h> 
#include <arpa/inet.h> 
#include <netinet/in.h> 

#define PORT     8000 

using namespace std;

static atomic_bool globalShutdown(false);

static void usbShutdownHandler(void *ptr) {
	(void) (ptr); // UNUSED.

	globalShutdown.store(true);
}

int main(void) 
{
	libcaer::devices::dvs128 dvs128Handle = libcaer::devices::dvs128(1, 0, 0, "");
	dvs128Handle.sendDefaultConfig();
	
	dvs128Handle.configSet(DVS128_CONFIG_BIAS, DVS128_CONFIG_BIAS_PR, 695);
	dvs128Handle.configSet(DVS128_CONFIG_BIAS, DVS128_CONFIG_BIAS_FOLL, 867);

	dvs128Handle.dataStart(nullptr, nullptr, nullptr, &usbShutdownHandler, nullptr);
	dvs128Handle.configSet(CAER_HOST_CONFIG_DATAEXCHANGE, CAER_HOST_CONFIG_DATAEXCHANGE_BLOCKING, true);

    int sockfd; 	 
	struct sockaddr_in servaddr; 
  	sockfd = socket(AF_INET, SOCK_DGRAM, 0);
	if (sockfd < 0){perror("socket creation failed"); exit(EXIT_FAILURE);} 
	memset(&servaddr, 0, sizeof(servaddr)); 	 
	servaddr.sin_family = AF_INET; 
	servaddr.sin_port = htons(PORT); 
	servaddr.sin_addr.s_addr = INADDR_ANY;
    bool flag = true;

    printf("Reading datas...\n");
	while (!globalShutdown.load(memory_order_relaxed)) 
	{
		std::unique_ptr<libcaer::events::EventPacketContainer> packetContainer = dvs128Handle.dataGet();
		if (packetContainer == nullptr){continue;}
		for (auto &packet : *packetContainer) 
		{
			if (packet == nullptr) {continue;}
			if (packet->getEventType() == POLARITY_EVENT) 
			{
		    int8_t arrayToSend[4 * packet->getEventNumber()];
				int32_t ts2;				
				std::shared_ptr<const libcaer::events::PolarityEventPacket> polarity = std::static_pointer_cast<libcaer::events::PolarityEventPacket>(packet);
					
				for(int16_t j = 0 ; j < packet->getEventNumber() ; j++)
				{
				  const libcaer::events::PolarityEvent &firstEvent = (*polarity)[j];

				  int8_t pol   = firstEvent.getPolarity();
				  uint8_t x = firstEvent.getX();
				  uint8_t y = firstEvent.getY();				  
				  int32_t ts1 = firstEvent.getTimestamp();
				  
          if (flag == true){ts2 = ts1; flag = false;}
          int8_t ts = ts1 - ts2;
					
					arrayToSend[j] = pol;
					arrayToSend[j + packet->getEventNumber()] = x;
					arrayToSend[j + (2 * packet->getEventNumber())] = y;
					arrayToSend[j + (3 * packet->getEventNumber())] = ts;

					ts2 = ts1;					
				  // printf("First polarity event - ts: %d, x: %d, y: %d, pol: %d.\n", ts, x, y, pol);
				}
        sendto(sockfd, arrayToSend, sizeof(arrayToSend), 0, (struct sockaddr *) &servaddr, sizeof(servaddr));
			}
		}
	}
	dvs128Handle.dataStop();
	printf("Shutdown successful.\n");
	return (EXIT_SUCCESS);
}
