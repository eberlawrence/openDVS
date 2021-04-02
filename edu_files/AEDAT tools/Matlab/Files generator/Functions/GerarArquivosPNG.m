function [] = GerarArquivosPNG(AEDAT, label, pathSaveData, timeStep )

    addpath('./Environment/');
    constantes = Constantes();
    qtdeImagens = constantes.tempoGravacao/(timeStep*10^-6);
    frames = GetFramesTimeSpaced(AEDAT,timeStep,'false');
    status = mkdir(strcat(pathSaveData,label));
    if(status == 1)
        for i = 1:qtdeImagens
            imwrite(frames{i+1},strcat(pathSaveData,label,'/',label,'_', int2str(i),'.png'));
        end
    end
end

