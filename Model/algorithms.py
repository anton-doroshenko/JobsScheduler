# This Python file uses the following encoding: utf-8
import os, sys
import numpy as np
import math
import csv
import random

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

def write_file(path, schedule, opt = 0):
    cur_opt = max_len(schedule, schedule.shape[1])[1]
    fieldnames = ["machine_%d" % i for i in range(schedule.shape[1])]
    fieldnames.insert(0, 'queue_num')
    print(fieldnames)
    print(cur_opt)
    row = {}
    with open(path, 'a+') as csvfile:
        csvfile.seek(0)
        if csvfile.readline() == '':
            csvfile.write("sep=,\n")
        csvfile.write("Идеальное время выполнения %d\n" % opt)
        csvfile.write("Текущее значение максимального времени выполнения: %d\n" % cur_opt)
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

def optimal(jobs, machines_quantity):
    return math.ceil(np.sum(jobs['time']) / machines_quantity)

def random_inicialisation(left_machines_quantity  = 4, right_machines_quantity = 5, left_jobs_quantity = 100, right_jobs_quantity = 300):
    machines_quantity = np.random.random_integers(left_machines_quantity, right_machines_quantity)
    jobs_quantity = np.random.random_integers(left_jobs_quantity, right_jobs_quantity)
    jobs = []
    for i in range(jobs_quantity):
        job = (i+1, np.random.random_integers(1, 30))
        jobs.append(job)
    jobs = np.array(jobs, dtype=[('index', '<i4'), ('time', '<i4')])
    print(jobs)
    return jobs, machines_quantity

def put_first_to_the_end(schedule, depth):
    row = schedule[depth,].tolist()
    row.append(row.pop(0))
    row = np.array(row, dtype=[('index', '<i4'), ('time', '<i4')])
    schedule[depth,] = row
    return schedule

def population_quantity(jobs_n, machines_quantity, probability):
    q = math.ceil(jobs_n / machines_quantity)
    n = 1 + math.log((1 / (1 - probability ** (1 / q))), machines_quantity)
    return math.ceil(n)

def mutation_probability(jobs_n, machines_quantity, population_quantity):
    q = math.ceil(jobs_n / machines_quantity)
    p = q * (1 - (1 - 10 * (1 / machines_quantity) ** (population_quantity - 1)) ** (1 / population_quantity))
    return p

def create_population(schedule, population_quantity, depth = 0, population = []):
    max_depth = schedule.shape[0] - 1
    machines_quantity = schedule.shape[1] - 1
    if len(population) >= population_quantity:
        return population
    if depth == 0:
        population = create_population(schedule, population_quantity, depth + 1, population)
    else:
        population.append(schedule.copy())
    if depth >= max_depth:
        return population
    else:
        for i in range(machines_quantity):
            schedule = put_first_to_the_end(schedule, depth)
            population = create_population(schedule, population_quantity, depth + 1, population)
        return population

def select_parents(population):
    parents = random.sample(population, 2)
    return parents
def crossoving(parents, queue_num):
    k = np.random.random_integers(1, queue_num)
    first_child = np.append(parents[0][0:k,], parents[1][k:,], axis = 0)
    second_child = np.append(parents[1][0:k,], parents[0][k:,], axis = 0)
    return first_child, second_child

def mutation(childs, p, queue_num, machines_quantity):
    for child in childs:
        if random.random() < p:
            queue = np.random.random_integers(1, queue_num - 1)
            mach_indexes = random.sample(range(machines_quantity), 2)
            temp = child[queue, mach_indexes[0]].copy()
            child[queue, mach_indexes[0]] = child[queue, mach_indexes[1]]
            child[queue, mach_indexes[1]] = temp
    return childs

def new_population(population, sizes, childs, machines_quantity):
    for child in childs:
        child_length = max_len(child, machines_quantity)[1]
        cur_max_length = max(sizes)
        cur_max_index = sizes.index(cur_max_length)
        if child_length < cur_max_length:
            population[cur_max_index] = child
            sizes[cur_max_index] = child_length

def genetic_algorithm(schedule, jobs_quantity, opt):
    queue_num = schedule.shape[0]
    machines_quantity = schedule.shape[1]
    n = population_quantity(jobs_quantity, machines_quantity, 0.7)#размер популяции
    p = mutation_probability(jobs_quantity, machines_quantity, n)#вероятность мутации
    population = create_population(schedule, n)
    sizes = []#список максимальных моментов окончания работ екземпляров популяции
    for item in population:
        sizes.append(max_len(item, machines_quantity)[1])
    for i in range(10):
        if opt in sizes:
            return population[sizes.index(opt)]
        parents = select_parents(population)
        childs = crossoving(parents, queue_num)
        childs = mutation(childs, p, queue_num, machines_quantity)
        new_population(population, sizes, childs, machines_quantity)
    return population[sizes.index(min(sizes))]

def main():
    #data = read_file('/media/anton/Ubuntu/GitWorkDir/JobsScheduler/tmp/input_data')
    data = random_inicialisation()
    jobs = data[0]
    machines_quantity = data[1]
    #jobs = np.array([(1, 1),(2, 2), (3, 3), (4, 4), (5, 5),
    #                 (6, 6), (7, 7), (8, 8), (9, 9), (10, 10),
    #                 (11, 11), (12, 12)],
    #                dtype=[('index', '<i4'), ('time', '<i4')])

    #machines_quantity = 3
    opt = math.ceil(np.sum(jobs['time']) / machines_quantity)
    schedule = spt_algorithm(jobs, machines_quantity)
    write_file("/home/anton/csvfile.csv", schedule, opt)
    print(schedule)
    print(opt)
    print()
    schedule_1 = schedule.copy()
    schedule_1 = swapping_method(schedule_1, len(jobs))
    print(schedule_1)
    print(schedule)
    print(max_len(schedule_1, machines_quantity)[1])
    print()
    schedule_2 = schedule.copy()
    schedule_2 = genetic_algorithm(schedule_2, len(jobs), opt)
    print(schedule_2)
    print(schedule)
    print(max_len(schedule_2, machines_quantity)[1])


    #print(schedule)
    #print()
    #print(opt, max_len(schedule, machines_quantity)[1])

    write_file("/home/anton/csvfile.csv", schedule_1, opt)
    write_file("/home/anton/csvfile.csv", schedule_2, opt)


if __name__ == "__main__":
    main()
