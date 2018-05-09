# This Python file uses the following encoding: utf-8
import os, sys
import numpy as np
import math
import csv

def read_file(path):
    jobs = []
    with open(path, 'r') as f:
        machines_quantity = int(f.readline().rstrip())
        for row in f:
            s = row.rstrip().split(' ')
            job = (int(s[0]), int(s[1]))
            jobs.append(job)
        jobs = np.array(jobs, dtype=[('index', '<i4'), ('time', '<i4')])
    return jobs, machines_quantity

def write_file(path, schedule):
    fieldnames = ["machine_%d" % i for i in range(schedule.shape[1])]
    fieldnames.insert(0, 'queue_num')
    print(fieldnames)
    row = {}
    with open(path, 'w') as csvfile:
        csvfile.write("sep=,\n")
        writer = csv.DictWriter(csvfile, fieldnames)
        writer.writeheader()
        for i in range(schedule.shape[0]):
            row[fieldnames[0]] = str(i)
            for j in range(len(fieldnames) - 1):
                if schedule[i][j]['time'] != 0:
                    row[fieldnames[j + 1]] = schedule[i][j]
                else:
                    row[fieldnames[j + 1]] = None
            writer.writerow(row)




def spt_algorithm(jobs, machines_quantity):
    '''
    spt(shortest processing time sequencing)
    Составляет начальное расписание выполнения работ
    с учетом минимизации среднего времени ожидания

    jobs - масив елеметы которого это кортежи которые
           содержат индекс работы и время ее выполнения
    machines_quantity - количество параллельных идентичных машин
    '''
    rows = math.ceil(len(jobs) / machines_quantity)     #максимальное количество работ выполняемых одной машиной
                                                        #math.ceil() - округление вверх

    schedule = np.zeros((rows, machines_quantity),                      #начальное расписание
                        dtype = [('index', '<i4'), ('time', '<i4')])    #елементы матрицы: индекс работы
                                                                        #и время ее выполнения
    jobs.sort(order='time')            #сортировать работы по времени их выполнения
    for i in range(len(jobs)):
        j = i // machines_quantity     #номер машины
        k = i % machines_quantity      #номер в очереди
        schedule[j][k] =  jobs[i]
    return schedule

def min_len(schedule, machines_quantity):
    min_index = 0
    min_sum = np.sum(schedule['time'][:, 0])
    for i in range(1, machines_quantity):
        cur_sum = np.sum(schedule['time'][:, i])
        if  cur_sum < min_sum:
            min_sum = cur_sum
            min_index = i
    return min_index, min_sum

def max_len(schedule, machines_quantity):
    max_index = 0
    max_sum = np.sum(schedule['time'][:, 0])
    for i in range(1, machines_quantity):
        cur_sum = np.sum(schedule['time'][:, i])
        if  cur_sum > max_sum:
            max_sum = cur_sum
            max_index = i
    return max_index, max_sum

def iteration_of_swapping_method(schedule, rows_quantity, columns_quantity, swapping_elements):
    '''
    '''
    min_len_index = min_len(schedule, columns_quantity)[0]#номер машины с наименьшим моментом выполнения работ
    max_len_index = max_len(schedule, columns_quantity)[0]#номер машины с наибольшим моментом выполнения работ
    len_1 = min_len(schedule, columns_quantity)[1]#момент окончания работ на машине с наименьшим моментом выполнения работ
    len_2 = max_len(schedule, columns_quantity)[1]#момент окончания работ на машине с наибольшим моментом выполнения работ
    swapping_elements['num_of_machine_1'] = min_len_index
    swapping_elements['num_of_machine_2'] = max_len_index
    for i in range(rows_quantity):
        time_1 = schedule['time'][i][min_len_index]#время выполнения работы, которая выполняется в i-ю очередь на машине с наименьшим моментом выполнения работ
        time_2 = schedule['time'][i][max_len_index]#время выполнения работы, которая выполняется в i-ю очередь на машине с наибольшим моментом выполнения работ
        delta = abs(len_1 - len_2 - 2 * (time_1 - time_2))
        if delta < swapping_elements['delta']:
            swapping_elements['num_in_queue'] = i
            swapping_elements['delta'] = delta
    if swapping_elements['delta'] < len_2 - len_1:
        p = swapping_elements['num_in_queue']
        r = swapping_elements['num_of_machine_1']
        s = swapping_elements['num_of_machine_2']
        temp = schedule[p, r].copy()
        schedule[p][r] = schedule[p][s]
        schedule[p][s] = temp
    swapping_elements['delta'] = float('Inf')

def add_swap_iteration(schedule):
    max = max_len(schedule, schedule.shape[1])
    min = min_len(schedule, schedule.shape[1])
    p = schedule.shape[0] - 1
    r = max[0]
    s = min[0]
    delta = abs(max[1] - min[1] - 2 * (schedule['time'][p][r] - schedule['time'][p-1][s]))
    if delta < max[1] - min[1]:
        temp = schedule[p, r].copy()
        schedule[p][r] = schedule[p - 1][s]
        schedule[p - 1][s] = temp

def swapping_method(schedule, jobs_quantity):
    '''
    Метод перестановок
    составляет расписание выполнения работ
    с минимальным максимальным моментом окончания работ

    schedule - начальное расписание выполнения работ
    '''
    rows_quantity = schedule.shape[0]#количество работ в очереди
    columns_quantity = schedule.shape[1]#количество машин
    cur_max_len = max_len(schedule, columns_quantity)[1]

    swapping_elements = {
        'num_in_queue': None,
        'num_of_machine_1': None,
        'num_of_machine_2': None,
        'delta': float('Inf')
    }
    i = 0
    while True:
        i += 1
        iteration_of_swapping_method(schedule, rows_quantity, columns_quantity, swapping_elements)
        new_max_len = max_len(schedule, columns_quantity)[1]
        if cur_max_len == new_max_len:
            break
        else:
            cur_max_len = new_max_len

    if jobs_quantity % columns_quantity != 0:
        add_swap_iteration(schedule)
        new_max_len = max_len(schedule, columns_quantity)[1]
        if cur_max_len != new_max_len:
            cur_max_len = new_max_len
            swapping_method(schedule, jobs_quantity)


    print('Iterations:', i)
    return schedule

def main():
    data = read_file('/home/anton/testfile')
    jobs = data[0]
    machines_quantity = data[1]
    #jobs = np.array([(1, 12),(2, 14), (3, 15), (4, 12), (5, 16),
    #                 (6, 12), (7, 12), (8, 23), (9, 13), (10, 15),
    #                 (11, 21), (12, 23), (13, 24), (14, 12), (15, 29)],
    #                dtype=[('index', '<i4'), ('time', '<i4')])

    #machines_quantity = 4
    opt = math.ceil(np.sum(jobs['time']) / machines_quantity)
    schedule = spt_algorithm(jobs, machines_quantity)
    print(schedule)
    print()
    schedule = swapping_method(schedule, len(jobs))
    print(schedule)
    print()
    print(opt, max_len(schedule, machines_quantity)[1])

    write_file("/home/anton/csvfile.csv", schedule)

if __name__ == "__main__":
    main()
