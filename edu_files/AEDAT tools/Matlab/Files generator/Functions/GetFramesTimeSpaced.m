function [ frames ] = GetFramesTimeSpaced( AEDAT, timeStep, boolean )
%{
This function get the AEDAT file and a value of time (us) and return the
frames who was formed by the sum of the spikes along th timeStamp (sorry my
english)
%}

[ t,to,tf,deltaT ] = GetTimeInformation( AEDAT );

[ xdim, ydim ] = DimensaoImagens( AEDAT );

[ numFrames,frameBoundaryTimes,numEvents ] = ...
    GetGeneralFrameInformation( AEDAT,timeStep );



frame = zeros([xdim,ydim,1])+ 0.5;
frames = {zeros(xdim,ydim)};
if(strcmp(boolean,'true'))
    figure();
end
for frameIndex = 1:numFrames
    
    firstIndex = find(t >= frameBoundaryTimes(frameIndex), 1, 'first');
    lastIndex = find(t <= frameBoundaryTimes(frameIndex + 1), 1, 'last');

    selectedLogical = [false(firstIndex - 1, 1); ...
                        true(lastIndex - firstIndex + 1, 1); ...
                        false(numEvents - lastIndex, 1)];

    eventsForFrame = struct;
    eventsForFrame.x = AEDAT.data.polarity.x(selectedLogical);
    eventsForFrame.y = AEDAT.data.polarity.y(selectedLogical);
    eventsForFrame.polarity = AEDAT.data.polarity.polarity(selectedLogical)-0.5;
    
    for i=1:length(eventsForFrame.x)
         frame(eventsForFrame.x(i,1)+1,eventsForFrame.y(i,1)+1) = ...
             frame(eventsForFrame.x(i,1)+1,eventsForFrame.y(i,1)+1) ...
             + eventsForFrame.polarity(i);  
    end
    
   

   frame = imrotate(frame,90);
   
   if(strcmp(boolean,'true'))
       imshow(frame);
   end
   
   frames = cat(4,frames,frame);
   
   frame = zeros([xdim,ydim,1]) + 0.5;
   
   
end 
end

