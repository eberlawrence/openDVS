import numpy as np
import pandas as pd
import random


#############################################################################################################
################################################# LOAD DATA #################################################
#############################################################################################################


subject_info = pd.read_csv('subject_info.csv', index_col=0)

input("\n\nPressione ENTER para iniciar.\n\n")

input("\nInsira os dados do voluntário solicitados.\n\n")


name = input("\nNome: ")
age = input("\nIdade: ")
gender = input("\nSexo: ")
system = input("\nSistema usado: ")

subject_info = subject_info.append({'Nome': name, 'Idade': age, 'Sexo': gender, "Sistema_usado": system}, ignore_index=True)

subject_info.to_csv("subject_info.csv")
print(subject_info)


#############################################################################################################
################################################# FIRST STEP ################################################
#############################################################################################################




input("\n\nIniciar o procedimento.\n\n")

object_list = ["Chave Allen", "Bola", "Bateria", "Garrafa", "Pincel", "Caixa", "Chave",
               "Calculadora", "Faca", "Câmera","Isqueiro", "Lata", "Lapiseira",
               "Estojo de óculos", "Caneta", "Pote", "Pendrive", "Copo", "Barbeador", "HD externo"]


object_list_tripod = object_list[::2]
object_list_power = object_list[1::2]


blocks = 5
objetcts_per_block = 6

block_list, sample_list = [], []
for i in range(blocks):
    for j in range(objetcts_per_block):
        block_list.append("BLOCO" + str(i + 1))
        sample_list.append(j)


columns = ['Objeto almejado', 'Preensão_Esperada', 'Preensão_Realizada', 'Angulação_Esperada', 'Angulação_Obtida', 'Tempo_Gasto', 'Objeto_Escorregou']
index = [block_list, sample_list]

subject_task_info_one = pd.DataFrame(columns=columns, index=index)

for i in range(blocks):
    print("\nLista de objetos 1 - Bloco " + str(i + 1) + " de " + str(blocks) + ".\n\n")
    input("\nPressione ENTER para continuar.\n\n")
    random.shuffle(object_list_tripod)
    random.shuffle(object_list_power)
    ordered_list = object_list_tripod[:int(objetcts_per_block/2)] + object_list_power[:int(objetcts_per_block/2)]
    random.shuffle(ordered_list)
    for j in range(objetcts_per_block):
        print("\nObjeto " + str(j + 1) + " de " + str(objetcts_per_block) + ":\n\n")
        angle = np.random.randint(-90,90)
        print("\nObjeto almejado: ", ordered_list[j])
        print("\nÂngulo do objeto: ", angle)
        input("\n\nPressione ENTER para continuar.\n")
        grasp_classified = input("\nPreensão realizada: ")
        angle_obtained = input("\nÂngulo obtido: ")
        time_spent = input("\nTempo gasto: ")
        object_slip = input("\nEscorregamento do objeto: ")
        subject_task_info_one.loc[('BLOCO' + str(i + 1), j), :] = {'Objeto almejado': ordered_list[j],
                                                                   'Preensão_Esperada': "Power" if object_list.index(ordered_list[j]) % 2 else "Tripod",
                                                                   'Preensão_Realizada': grasp_classified,
                                                                   'Angulação_Esperada': angle,
                                                                   'Angulação_Obtida': angle_obtained,
                                                                   'Tempo_Gasto': time_spent,
                                                                   'Objeto_Escorregou': object_slip}

        input("\nPressione ENTER para continuar.\n\n")
    print(subject_task_info_one)
    print("\n\nBloco " + str(i + 1) + " finalizado!\n\n")
    input("\nPressione ENTER para continuar.\n\n")


subject_task_info_one.to_csv(str(name) + "_task_info_one.csv", sep='\t', encoding='utf-8')

print("\n\nDados coletados com sucesso!\n\n")
input("\nPressione ENTER para finalizar a coleta.\n\n")
