function [ numFrames,frameBoundaryTimes,numEvents ] = ...
    GetGeneralFrameInformation( AEDAT,timeStep)
%{
    Essa função tem por objetivo retornar dados gerais sobre a formação de
    frames limitados por tempo.
    ---ENTRADA---
    AEDAT - arquivo AEDAT;
    timeStep - intervalo de tempo em que será acumulado os spikes para
    geração de um frame;
    ---SAÍDA---
    numFrames - é a quantidade de frames dado o tempo total da gravação e o
    timeStep;
    frameBoundaryTimes - vetor com limites iniciais e finais de tempo em
    que serão gerados frames da gravação original
    numEvents - quantidade de eventos totais de uma gravação
%}

[ t,to,tf,deltaT ] = GetTimeInformation( AEDAT );

numFrames = deltaT/timeStep;
frameTimes = to + timeStep*0.5 : timeStep : tf;
frameBoundaryTimes = [to frameTimes + timeStep * 0.5];
numEvents = length(t);

end

