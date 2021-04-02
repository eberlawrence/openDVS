function [ t,to,tf,deltaT ] = GetTimeInformation( AEDAT )


t = AEDAT.data.polarity.timeStamp;
to = min(AEDAT.data.polarity.timeStamp); 
tf = max(AEDAT.data.polarity.timeStamp); 
deltaT = (tf - to); 

end

