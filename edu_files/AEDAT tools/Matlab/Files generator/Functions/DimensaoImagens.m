function [ xdim, ydim ] = DimensaoImagens( AEDAT )
%UNTITLED4 Summary of this function goes here
%   Detailed explanation goes here
xdim = AEDAT.info.deviceAddressSpace(2);
ydim = AEDAT.info.deviceAddressSpace(1);

end

