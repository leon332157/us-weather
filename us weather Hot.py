# coding=utf8
print('Loading')
import os, time, webbrowser, threading, json, echarts
from functools import partial
from operator import itemgetter

global min_list
global headers
global state_choice
state_detail = []
state_dict = {}
city_dict = {}
headers = {
    'User-Agent': 'Mozilla/5.0'}  # using requests to get website will use a 'python-request' UA, we need to change.
min_list = []
try:
    from bs4 import BeautifulSoup as bs
    import requests
except ImportError as e:
    print(e)
    print('Module not installed, please use "Module Install.py" to install module as superuser!')
    exit(1)


def check_everything():
    global city_sort_list
    global state_abbrev_full
    global state_full_abbrev
    print('Getting state list from Github...')
    state_full_abbrev = json.loads(requests.get(
        'https://raw.Githubusercontent.com/leon332157/us-weather/master/data/state.json').content.decode('utf8'))
    state_abbrev_full = {}
    for each in state_full_abbrev:
        state_abbrev_full[state_full_abbrev.get(each)] = each
    print('Getting city list from Github...')
    city_sort_list = json.loads(requests.get(
        'https://raw.Githubusercontent.com/leon332157/us-weather/master/data/city.json').content.decode('utf8'))


def get_state():
    print('Getting states from website...')
    raw_content = requests.get('http://www.accuweather.com/en/browse-locations/nam/us', headers=headers)
    content = raw_content.content
    soup1 = bs(content, 'html.parser')
    state_list = soup1.find_all('ul', class_="articles")
    soup2 = bs(str(state_list[0]), 'html.parser')
    state_detail = soup2.find_all('a')
    state_detail.pop()
    for each in state_detail:
        soup3 = bs(str(each), 'html.parser')
        state_name = str(str(soup3.find('em', text=True)).replace('<em>', '')).replace('</em>', '')
        state_link = str(each).split('"')
        state_dict[state_name] = state_link[1]
    print('Successful')
    return state_dict


def select_state():
    while True:
        choice = str(input('Input abbreviation of a state or all=all states States list=h e=exit >>>'))
        if choice == 'h':
            for key, value in state_full_abbrev.items():
                print(str(key) + ' ' + str(value))
        elif choice == 'all':
            return 'all'
        elif choice == 'e':
            exit(0)
        elif choice == 'exit':
            exit(0)
        else:
            if not choice == '':
                state_choice = state_abbrev_full.get(choice.upper())
                if not state_choice == None:
                    if state_choice == 'District of Columbia a.k.a. Washington DC':
                        cho = input('Sure? Your input: ' + choice + ' Referred as: ' + str(
                            state_abbrev_full.get(choice.upper())) + ' (y/n):')
                        if cho == 'y':
                            return 'District of Columbia'
                        elif cho == 'n':
                            return
                        else:
                            print('Invald choice!')
                            return
                    else:
                        cho = input('Sure? Your input: ' + choice + ' Referred as: ' + str(
                            state_abbrev_full.get(choice.upper())) + ' (y/n):')
                        if cho == 'y':
                            return state_choice
                        elif cho == 'n':
                            return
                        else:
                            print('Invald choice!')
                            return
                else:
                    print('Please input a valid choice!')
                    return None


def get_city(state_dict, state_choice, thr, range1, range2):
    '''I've tried my best to get it faster, though there are more than 5000 items in the city dict
    I use multi thread for faster program speed, but it more depends on your network speed :('''
    listt = []
    for key, value in state_dict.items():
        listt.append(key)
    if state_choice == None:
        for ea in listt[range1:range2]:
            print('Getting city for ' + ea + ' in thread:' + str(thr))
            raw_content = requests.get(state_dict.get(ea), headers=headers)
            content = raw_content.content
            soup4 = bs(content, "html.parser")
            city_list = soup4.find_all('ul', class_="articles")[0]
            city_detail = city_list.find_all('a')
            city_detail.pop()
            for each in city_detail:
                city_name = str(each.find('em', text=True)).replace('<em>', '').replace('</em>', '')
                city_link = str(each).split('"')
                city_dict[city_name + ', ' + str(ea)] = city_link[1]
        return city_dict
    else:
        print('Getting city for ' + state_choice)
        raw_content = requests.get(state_dict.get(state_choice), headers=headers)
        content = raw_content.content
        soup4 = bs(content, "html.parser")
        city_list = soup4.find_all('ul', class_="articles")[0]
        city_detail = city_list.find_all('a')
        city_detail.pop()
        for each in city_detail:
            city_name = str(each.find('em', text=True)).replace('<em>', '').replace('</em>', '')
            city_link = str(str(each).split('"')[1])
            city_dict[city_name + ', ' + str(state_choice)] = city_link
        print(str(state_choice) + ' --> Done! :)')
        return city_dict


def get_temp_thread(range1, range2, thr, real_nor, f_c):
    choice = city_sort_list[range1:range2]
    for each in choice:
        city = each.get(u'city')
        state = each.get(u'state')
        get = '%s, %s' % (city, state)
        print('Getting temperature for ' + get + ' in thread:' + str(thr))
        try:
            link = city_dict[get]
        except Exception as e:
            print('City %s Not found. Passing...' % get)
            continue
        raw_content = requests.get(link, headers=headers)
        content = raw_content.content
        soup7 = bs(content, 'html.parser')
        temp = str(soup7.find_all('span', class_="large-temp")[0]).replace('<span class="large-temp"',
                                                                           '').replace(
            '>',
            '').replace(
            '</span', '').replace('°', '')
        real = str(soup7.find_all('span', class_="realfeel")[0]).replace('<span class="realfeel"',
                                                                         '').replace(
            '>',
            '').replace(
            '</span', '').replace('RealFeel®', '').replace('°', '')
        if real_nor == 'y':
            if f_c == 'c':
                reall = f_to_c(real)
                min_list.append({'city': get, 'min': reall})
            else:
                min_list.append({'city': get, 'min': real})
        else:
            if f_c == 'c':
                tempp = f_to_c(temp)
                min_list.append({'city': get, 'min': int(tempp)})
            else:
                min_list.append({'city': get, 'min': int(temp)})
    return min_list, f_c


def f_to_c(temp):
    c = str('{:.1f}').format(5.0 / 9.0 * (float(float(temp) + 0.0) - 32.0))
    return c


def process_everything(min_list):
    global sorted_min_list
    global final_min
    global final_city
    print('Processing data...')
    final_min = []
    final_city = []
    sorted_min_list = sorted(min_list, key=lambda x: float(itemgetter("min")(x)), reverse=True)
    for each in sorted_min_list:
        final_city.append(each['city'])
        final_min.append(each['min'])
    print('Done! :)')
    print('Total city processed: {}'.format(len(sorted_min_list)))
    print('Hottest City: ' + sorted_min_list[1]['city'])


def graph(temp_unit, real, state):
    print('Total city in graph: {}'.format(len(final_city)))
    if temp_unit == 'c':
        del temp_unit
        temp_unit = 'Celsius'
        temp_unit_abbr = 'C'
    else:
        del temp_unit
        temp_unit = 'Fahrenheit'
        temp_unit_abbr = 'F'
    if real == 'y':
        del real
        real = 'Yes'
    else:
        del real
        real = 'No'
    canvas = echarts.Echart('Hot?', 'Temp unit: ' + temp_unit + ' RealFeel: ' + real, html_title='Hot?')
    canvas.use(echarts.Axis('category', 'bottom', data=final_city))
    canvas.use(echarts.Bar(data=final_min))
    canvas.use(echarts.Tooltip(trigger='item'))
    name_graph = '/Hot {0} {1}'.format(state, temp_unit_abbr)
    canvas.save(path=os.getcwd(), name=name_graph)
    saved_graph_path = os.getcwd() + '/Hot {0} {1}{2}'.format(state, temp_unit_abbr, '.html')
    print('Saved to: {0} {1}'.format(saved_graph_path, ':)'))
    while True:
        openn = str(input('Open ' + saved_graph_path + ' (y/n):'))
        if openn == 'y':
            webbrowser.open('file://' + saved_graph_path)
            exit(0)
        elif openn == 'n':
            exit(0)
        else:
            print('Invalid choice')
            continue


def choose():
    global real_nor
    global f_c
    while True:
        real_nor = str(input('Do you want RealFeel® by Accuweather?(y/n):'))
        if real_nor == 'y':
            break
        elif real_nor == 'n':
            break
        else:
            print('Please Input a Valid Choice!')
            continue
    while True:
        f_c = str(input('Fahrenheit or Celsius(F/C):'))
        if f_c == 'F':
            f_c=f_c.lower()
            break
        elif f_c == 'f':
            break
        elif f_c == 'C':
            f_c=f_c.lower()
            break
        elif f_c == 'c':
            f_c.upper()
            break
        else:
            print('Please Input a Valid Choice!')
            continue


check_everything()
get_state()
while True:
    state_choice = select_state()
    if state_choice is None:
        continue
    else:
        break
if state_choice == 'all':
    th1 = threading.Thread(target=partial(get_city, state_dict, None, 1, 0, 10), name='th1')
    th2 = threading.Thread(target=partial(get_city, state_dict, None, 2, 10, 21), name='th2')
    th3 = threading.Thread(target=partial(get_city, state_dict, None, 3, 21, 31), name='th3')
    th4 = threading.Thread(target=partial(get_city, state_dict, None, 4, 31, 42), name='th4')
    th5 = threading.Thread(target=partial(get_city, state_dict, None, 5, 42, 51), name='th5')
    th = [th1, th2, th3, th4, th5]
    tm1 = time.time()
    for each in th:
        each.start()
        time.sleep(0.001)
    for each in th:
        each.join()
    print('seconds used: ' + str(int(time.time() - tm1 - 0.001 * 4)))  # calculate time difference

    choose()

    t1 = threading.Thread(target=partial(get_temp_thread, 0, 12, 1, real_nor, f_c), name='t1')
    t2 = threading.Thread(target=partial(get_temp_thread, 12, 24, 2, real_nor, f_c), name='t2')
    t3 = threading.Thread(target=partial(get_temp_thread, 24, 48, 3, real_nor, f_c), name='t3')
    t4 = threading.Thread(target=partial(get_temp_thread, 48, 48 + 12, 4, real_nor, f_c), name='t4')
    t5 = threading.Thread(target=partial(get_temp_thread, 60, 72, 5, real_nor, f_c), name='t5')
    t6 = threading.Thread(target=partial(get_temp_thread, 72, 84, 6, real_nor, f_c), name='t6')
    t7 = threading.Thread(target=partial(get_temp_thread, 84, 96, 7, real_nor, f_c), name='t7')
    t8 = threading.Thread(target=partial(get_temp_thread, 96, 108, 8, real_nor, f_c), name='t8')
    t9 = threading.Thread(target=partial(get_temp_thread, 108, 120, 9, real_nor, f_c), name='t9')
    t = [t1, t2, t3, t4, t5, t6, t7, t8, t9]
    tm2 = time.time()
    for each in t:
        each.start()
    for each in t:
        each.join()
    timer = int(time.time() - tm2 - 0.001 * 9)  # calculate time difference
    if timer < 60:
        print('seconds used: ' + str(timer))
    else:
        print('minutes used: ' + str(timer // 60))
    process_everything(min_list)
    graph(f_c, real_nor, state_choice)
else:
    content_dict = {}

    def get_temp(city_dict):
        for city_state, link in city_dict.items():
            city = city_state.split(',')[0]
            state = city_state.split(', ')[1]
            get = '%s, %s' % (city, state)
            print('Getting temperature for ' + get)
            link = city_dict[get]
            raw_content = requests.get(link, headers=headers)
            content = raw_content.content
            content_dict[get] = content
        return content_dict


    def parse_content(content_dict, real_nor, f_c):
        for city_state, content in content_dict.items():
            city = city_state.split(', ')[0]
            state = city_state.split(', ')[1]
            get = '%s, %s' % (city, state)
            print('Phrasing content for %s' % get)
            soup7 = bs(content, 'html.parser')
            temp = str(soup7.find_all('span', class_="large-temp")[0]).replace('<span class="large-temp"',
                                                                               '').replace(
                '>',
                '').replace(
                '</span', '').replace('°', '')
            real = str(soup7.find_all('span', class_="realfeel")[0]).replace('<span class="realfeel"',
                                                                             '').replace(
                '>',
                '').replace(
                '</span', '').replace('RealFeel®', '').replace('°', '')
            if real_nor == 'y':
                if f_c == 'c':
                    reall = f_to_c(real)
                    min_list.append({'city': get, 'min': reall})
                else:
                    min_list.append({'city': get, 'min': real})
            else:
                if f_c == 'c':
                    tempp = f_to_c(temp)
                    min_list.append({'city': get, 'min': int(tempp)})
                else:
                    min_list.append({'city': get, 'min': int(temp)})
        return min_list


    get_city(state_dict, state_choice, None, None, None)
    choose()
    tm1 = time.time()
    get_temp(city_dict)
    print('seconds used: ' + str(int(time.time() - tm1)))  # calculate time difference
    tm2 = time.time()
    parse_content(content_dict, real_nor, f_c)
    print('seconds used: ' + str(int(time.time() - tm2)))  # calculate time difference
    process_everything(min_list)
    graph(f_c, real_nor, state_choice)
