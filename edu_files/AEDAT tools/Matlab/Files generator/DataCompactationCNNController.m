%{ 
Universidade Federal de Uberl�ndia
Laborat�rio de Engenharia Biom�dica - BioLab

Autor: Eduardo Borges Gouveia

Esse script � respons�vel exportar imagens png, gravados por uma camera
Neurom�rfica para o formato .mat.
A estrutura armazenada consiste em uma matriz M-by-N onde M repre-
senta a quantidades de imagens e N � o produto A*B da imagem original
A-by-B
%}

clc;
clear all;
close all;

addpath('Functions/');

path = 'C:/Users/Samsung/Documents/Mestrado/HandStuff/Datasource/PNG_files/';

%% Labels
biolab128_label = {...
    ;'Cubo'...
    ;'Lapiseira'...
    ;'Mouse'...
    };

save(strcat('C:/Users/Samsung/Documents/Mestrado/HandStuff/Datasource/MAT_files/','batche_label'),'biolab128_label');

%% DataSet
timeStep = 300000;
constantes = Constantes();
numImagens = constantes.tempoGravacao/(timeStep*10^-6);
numClasses = length(biolab128_label);
parcelaTreino = 0.9;
indexTreino = 1;
indexTeste = 1;

for j = 1:numClasses
    fullPath = strcat(path, biolab128_label{j});
    for i = 1:numImagens
        if(i < parcelaTreino*numImagens)
            frame = imread(strcat(fullPath,'/',biolab128_label{j},'_',int2str(i),'.png'));
            dataTreino(indexTreino,:) = vertcat(frame(:), j);
            indexTreino = indexTreino + 1;
        else
            frame = imread(strcat(fullPath,'/',biolab128_label{j},'_',int2str(i),'.png'));
            dataTeste(indexTeste,:) = vertcat(frame(:), j);
            indexTeste = indexTeste + 1;
        end
    end
end

%% Separando e embaralhando os arquivos

% dataSet para teste
dataTeste = sortrows(dataTeste);
data = dataTeste(:,1:end-1);
labels = dataTeste(:,end);
batch_label = 'dataSet de testes';
save(strcat('C:/Users/Samsung/Documents/Mestrado/HandStuff/Datasource/MAT_files/','biolab128_dataTeste'),'data','labels','batch_label');

% dataSet para treino
dataTreino = sortrows(dataTreino);
data = dataTreino(:,1:end-1);
labels = dataTreino(:,end);
batch_label = 'dataSet de treino';
save(strcat('C:/Users/Samsung/Documents/Mestrado/HandStuff/Datasource/MAT_files/','biolab128_dataTreino'),'data','labels','batch_label');


%% write an txt file
fid=fopen('C:/Users/Samsung/Documents/Mestrado/HandStuff/Datasource/MAT_files/README.txt','wt');
fprintf(fid, ['------------------- README -------------------' '\r\n']);
fprintf(fid, ['FILES GENERATED BY SCRIPT' '\r\n']);
fprintf(fid, ['Date: ' date '\r\n']);
fprintf(fid,['timeStep: ' int2str(timeStep) ' [us] \r\n']);
fprintf(fid,['origin path of PNG files: ' path '\r\n']);
constantes = Constantes();
fprintf(fid,['full time of records: ' int2str(constantes.tempoGravacao) ' [s] \r\n']);
fprintf(fid,['amount of record in each class: '  int2str(constantes.tempoGravacao/(timeStep*10^-6)) ' [un] \r\n']);
fprintf(fid,['degrees between images: '  num2str(360.0 / (constantes.tempoGravacao/(timeStep*10^-6))) ' [�] \r\n']);
fprintf(fid,['percent of images used by trainning: '  num2str(parcelaTreino) ' [percent] \r\n']);
fprintf(fid,['amount of images used by trainning: '  num2str(parcelaTreino*numImagens) ' [un] \r\n']);
fprintf(fid,['percent of images used by testing: ' num2str(1-parcelaTreino) ' [percent] \r\n']);
fprintf(fid,['amount of images used by testing: ' num2str((1-parcelaTreino)*numImagens) ' [un] \r\n']);
fprintf(fid,['total of images generated: ' num2str(numImagens*length(biolab128_label)) ' [un] \r\n']);
fprintf(fid,['total of images used by trainning: ' num2str(parcelaTreino*numImagens*length(biolab128_label)) ' [un] \r\n']);
fprintf(fid,['total of images used by testing: ' num2str((1-parcelaTreino)*numImagens*length(biolab128_label)) ' [un] \r\n']);
for i=1:length(biolab128_label)
    fprintf(fid,['files used to generate data:' biolab128_label{i} '\r']);    
end
fclose(fid);true