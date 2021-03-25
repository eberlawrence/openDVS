import numpy as np
import pandas as pd
import random

subject_info = pd.read_csv('subject_info.csv', sep='\t', encoding='utf-8', index_col=0)


input("\n\nPressione ENTER para iniciar.\n\n")

input("\nInsira os dados do voluntário solicitados.\n\n")


name = input("\nNome: ")
age = input("\nIdade: ")
gender = input("\nSexo: ")

subject_info = subject_info.append({'Nome': name, 'Idade': age, 'Sexo': gender}, ignore_index=True)

subject_info.to_csv("subject_info.csv", sep='\t', encoding='utf-8')
print(subject_info)


object_list_one = ["Caneta", "Copo", "Colher", "Garrafa", "Chave", "Caixa", "Faca", "Celular",
                   "Barbeador", "Lata de bebida", "Chave de fenda", "Bola", "Escova de dentes",
                   "Pote", "Parafuso", "Carteira", "Isqueiro", "Pêra", "Chave Allen", "Laranja"]
object_list_one_tripod = object_list_one[::2]
object_list_one_power = object_list_one[1::2]


object_list_two = ["Chave fixa", "Estojo de óculos", "Lapiseira", "Lâmpada",
                   "Pen drive", "Calculadora", "Pincel", "HD", "Pilha", "Câmera"]
object_list_two_tripod = object_list_two[::2]
object_list_two_power = object_list_two[1::2]

input("\n\nIniciar a primeira etapa do procedimento.\n\n")

blocks = 2
objetcts_per_block = 4

block_list, sample_list = [], []
for i in range(blocks):
    for j in range(objetcts_per_block):
        block_list.append("BLOCO" + str(i + 1))
        sample_list.append(j)


columns = ['Preensão_Esperada', 'Preensão_Classificada', 'Angulação_Esperada', 'Angulação_Obtida', 'Tempo_Gasto', 'Objeto_Escorregou']
index = [block_list, sample_list]

subject_task_info_one = pd.DataFrame(columns=columns, index=index)

a = pd.DataFrame(columns=["A", "B", "C", "D"], index=[np.array(["BLOCO1", "BLOCO1", "BLOCO2"]), np.array([1,2,1])])

for i in range(blocks):
    print("\nLista de objetos 1 - Bloco " + str(i + 1) + " de " + str(blocks) + ".\n\n")
    input("\nPressione ENTER para continuar.\n\n")
    random.shuffle(object_list_one_tripod)
    random.shuffle(object_list_one_power)
    ordered_list = object_list_one_tripod[:int(objetcts_per_block/2)] + object_list_one_power[:int(objetcts_per_block/2)]
    random.shuffle(ordered_list)
    for j in range(objetcts_per_block):
        print("\nObjeto " + str(j + 1) + " de " + str(objetcts_per_block) + ":\n\n")
        angle = np.random.randint(-90,90)
        print("\nObjeto almejado: ", ordered_list[j])
        print("\nÂngulo do objeto: ", angle)
        input("\n\nPressione ENTER para continuar.\n")
        grasp_classified = input("\nPreensão classificada: ")
        angle_obtained = input("\nÂngulo obtido: ")
        time_spent = input("\nTempo gasto: ")
        object_slip = input("\nEscorregamento do objeto: ")
        subject_task_info_one.loc[('BLOCO' + str(i + 1), j), :] = {'Preensão_Esperada': "Power" if object_list_one.index(ordered_list[j]) % 2 else "Tripod",
                                                      'Preensão_Classificada': grasp_classified,
                                                      'Angulação_Esperada': angle,
                                                      'Angulação_Obtida': angle_obtained,
                                                      'Tempo_Gasto': time_spent,
                                                      'Objeto_Escorregou': object_slip}

        input("\nPressione ENTER para continuar.\n\n")
    print(subject_task_info_one)
    print("\n\nBloco " + str(i + 1) + " finalizado!\n\n")
    input("\nPressione ENTER para continuar.\n\n")


subject_task_info_one.to_csv(str(name) + "_task_info_one.csv", sep='\t', encoding='utf-8')
