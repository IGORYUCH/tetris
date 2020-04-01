import pygame
from copy import deepcopy  # нужен для "глубокого" копирования списков
from random import choice

class Base_field:
    def change_color(self,rect_list,color):# своеобразный сеттер для изменения цвета квадратов
        for rect in rect_list:
            self.field[rect[1]][rect[0]] = color  


class Figure:
    def __init__(self, coords, clr):
        self.rects_coords = coords #список коордитат квадратов, относящихся к финуре в данный момент
        self.figure_index = random_figures.index(coords)
        self.color = clr # цвет используемый для закраски квадратов
        self.orig_figure = deepcopy(coords)
        self.rotate_status = 0 
        self.was_swapped = False

    def fall(self): # перемещает фигуру вниз
        tetris_field.change_color(self.rects_coords,tetris_field.color)#затираем стандартным цветом предыдущие квадраты, занятые фигурой
        for rect in self.rects_coords:
            rect[1] += 1# меняем координату Y каждого квадрата фигуры
        tetris_field.change_color(self.rects_coords,self.color)#закрашиваем в цвет фигуры новые ее квадраты
       
    def is_overlayed(self, rect_list):#Метод, необходимый для проверки наложения новой фигуры на непустые квадраты
        for rect in rect_list:
            # Если в указанных координатах находится пустота или указанные координаты в списке координат квадратов фигуры...
            if not ((tetris_field.field[rect[1]][rect[0]] == tetris_field.color) or ([rect[0],rect[1]] in self.rects_coords)):
                break
        else:
            return False

    def is_overlayed2(self,rect_list):
        for rect in rect_list:
            if not (tetris_field.field[rect[1]][rect[0]] == tetris_field.color):
                return True
        else:
            return False

    def move(self,direction):# перемещает фигуру влево - вправо
        x_cords = [i[0] for i in self.rects_coords]
        figure_max_x, figure_min_x = max(x_cords), min(x_cords)
        if (figure_max_x+direction <= len(tetris_field.field[0])-1) and (figure_min_x-1 >= 0 or direction > 0):# если максимальный х квадрата фигуры больше длины строки х-1...
            rects_plus_d = [[rect[0]+direction, rect[1]] for rect in deepcopy(self.rects_coords)] # Создаем копию исходного массива и увеличиваем каждый x на ведичину direction
            if self.is_overlayed(rects_plus_d) == False:#Если перемещенная фигура не накладывается на непустые квадраты...
                move_sound.play()
                tetris_field.change_color(self.rects_coords, tetris_field.color)
                self.rects_coords = rects_plus_d
                tetris_field.change_color(self.rects_coords, self.color)
            
    def rotate(self):# Метод поворота фигуры
        rotated_fig = deepcopy(self.rects_coords)# Сначала сделаем копию фигуры, повернем ее и проверим, не вылезает ли она за границы поля...
        for index in range(len(self.rects_coords)):
            rotated_fig[index][0] += figure_rotate[self.figure_index][self.rotate_status][index][0]# Применяем правило поворота для x
            rotated_fig[index][1] += figure_rotate[self.figure_index][self.rotate_status][index][1]# Применяем правило поворота для y
        x_coords = [i[0] for i in rotated_fig]
        y_coords = [j[1] for j in rotated_fig]
        max_x, max_y = max(x_coords), max(y_coords)
        min_x, min_y = min(x_coords), min(y_coords)
        if (min_y >= 0) and (min_x >= 0) and (max_x <= len(tetris_field.field[0])-1) and (max_y <= len(tetris_field.field)-1):
            if self.is_overlayed(rotated_fig) == False:#Если повернутая фигура не накладывается на непустые квадраты...
                rot_sound.play()
                tetris_field.change_color(self.rects_coords, tetris_field.color)
                self.rects_coords = deepcopy(rotated_fig)# Если все условия соблюдены, Делаем копию основной фигурой
                self.rotate_status += 1# После успешного поворота увеличиваем статус поворота
                if self.rotate_status == len(figure_rotate[self.figure_index]):# если было было применено последнее правило поворота, то фигура в исходнои положении
                    self.rotate_status = 0
                tetris_field.change_color(self.rects_coords, self.color)
                
    def update_figure(self):#Замена фигуры на новую с новым цветом
        self.rects_coords = deepcopy(next_fig.figure)# Выбыр новой фигуры
        self.orig_figure = deepcopy(next_fig.figure)
        self.color = next_fig.color# Новый цвет
        self.figure_index = random_figures.index(self.rects_coords)# новый индекс правила вращения, в сответствии с выбранной фигурой
        self.rotate_status = 0 # Обнуляем статус вращения
        self.was_swapped = False
        if self.is_overlayed2(self.rects_coords) == True:
            return 1#Если при обновлении фигура накладывается, возвращаем 1
        
    def get_collision(self):#Метод проверки состояния под фигурой и если нужно выбор новой фигуры
        y_coords = [i[1] for i in self.rects_coords]
        y_max = max(y_coords)
        bottom_rects = []
        for rect in self.rects_coords:
            if rect[1] == y_max:
                bottom_rects.append(rect[:])
        for bottom_rect in bottom_rects:
            if bottom_rect[1] == len(tetris_field.field)-1:#Проверка на достижения ДНА. Иначе проверка состояния квадрата внизу
                tetris_field.strip_completed_lines()
                if self.update_figure() == 1:
                    return 1
                next_fig.update_figure()
                break
            else:
                for rect in self.rects_coords:
                    # Если клетка под квадратом не пустая и не входит в число клеток фигуры...
                    if tetris_field.field[rect[1]+1][rect[0]] != tetris_field.color and ([rect[0], rect[1]+1] not in self.rects_coords):
                        tetris_field.strip_completed_lines()
                        if self.update_figure() == 1:
                            return 1#Если фигура наложилась при обновлении, возвращаем 1
                        next_fig.update_figure()
                        break

    def swap(self):#Меняет фигуру на удерживаемую
        if self.was_swapped == False:
            swap_sound.play()
            if swap_fig.printed_figure == [[0, 0]]:#Если фигура в свапе изначально пустая...
                swap_fig.figure = deepcopy(self.orig_figure)
                swap_fig.color = self.color
                swap_fig.printed_figure = [[printed_crds[0]-5, printed_crds[1]+1] for printed_crds in deepcopy(self.orig_figure)]
                swap_fig.change_color(swap_fig.printed_figure, swap_fig.color)
                tetris_field.change_color(self.rects_coords, AIR_COLOR)
                self.update_figure()
            else:
                tetris_field.change_color(self.rects_coords, AIR_COLOR)
                swap_fig.change_color(swap_fig.printed_figure, AIR_COLOR)
                new_fig = deepcopy(swap_fig.figure)#Сохраняем в промежуточную переменную координаты квадратов свап фигуры
                new_color = swap_fig.color#Сохраняем в промежуточную переменную цвет свап фигуры
                swap_fig.figure = deepcopy(self.orig_figure)
                swap_fig.color = self.color
                swap_fig.printed_figure = [[printed_crds[0]-5, printed_crds[1]+1] for printed_crds in deepcopy(swap_fig.figure)]
                swap_fig.change_color(swap_fig.printed_figure, swap_fig.color)
                self.orig_figure = deepcopy(new_fig)
                self.rects_coords = deepcopy(new_fig)
                self.color = new_color
                self.rotate_status = 0
                self.figure_index = random_figures.index(new_fig)
                tetris_field.change_color(self.rects_coords, self.color)
            self.was_swapped = True
    

class Field(Base_field):
    def __init__(self, color):
         self.color = color
         self.field = [[self.color for j in range(t_cells_x)] for i in range(t_cells_y)] #генератор двухмерного массива

    def strip_completed_lines(self):#Метод отвечающий за очиску заполненных линий и перемещение вниз квадратов, находившихся над этой линией
        global score
        line_length = len(self.field[0])
        for line in range(len(self.field)):
            for rect in range(line_length):# Цикл проверяющий очередную линию поля на завершенность
                if self.field[line][rect] == self.color:
                    break
            else:
                strip_line_sound.play()
                self.field[line] = deepcopy([self.color for i in range(line_length)])#Заполняем завершенную линию пустыми квадратами
                for new_line in range(line-1, -1, -1):#Цикл по всем линиям выше текущей завершенной линии
                    for new_rect in range(line_length):
                        if self.field[new_line][new_rect] != self.color:
                            self.field[new_line+1][new_rect] = self.field[new_line][new_rect]
                            self.field[new_line][new_rect] = self.color
                score += t_cells_x*10

    def reset(self):# Закрашивает в стандартный цвет все поле
        for line in range(len(self.field)):
            for rect in range(len(self.field[0])):
                self.field[line][rect] = self.color


class Next_fig(Base_field):  # класс новой фигуры и класс удерживаемой фигуры
    def __init__(self, new_coords, new_clr):
        self.field = [[tetris_field.color for j in range(4)] for i in range(3)]
        self.figure = new_coords
        self.printed_figure = [[printed_crds[0]-5, printed_crds[1]+1] for printed_crds in deepcopy(self.figure)]
        self.color = new_clr

    def update_figure(self):
        self.change_color(self.printed_figure, AIR_COLOR)
        self.figure = deepcopy(choice(random_figures))
        self.printed_figure = [[printed_crds[0]-5, printed_crds[1]+1] for printed_crds in deepcopy(self.figure)]
        self.color = choice(random_colors)
        self.change_color(self.printed_figure, self.color)


class Swap_fig(Base_field):  # класс новой фигуры и класс удерживаемой фигуры
    def __init__(self):
        self.field = [[tetris_field.color for j in range(4)] for i in range(3)]
        self.figure = [[5, -1]]
        self.printed_figure = [[printed_crds[0]-5,printed_crds[1]+1] for printed_crds in deepcopy(self.figure)]
        self.color = AIR_COLOR

    def update_figure(self):
        self.change_color(self.printed_figure, AIR_COLOR)
        self.figure = [[5, -1]]
        self.printed_figure = [[printed_crds[0]-5, printed_crds[1]+1] for printed_crds in deepcopy(self.figure)]
        self.color = AIR_COLOR


def animate():# функция, отвечающая за отрисовку всех элементов игры
    for y in range(len(tetris_field.field)):# цикл по всем квадратом поля.Каждый элемент этого списка содержит цвет квадрата
        for x in range(len(tetris_field.field[y])):
            pygame.draw.rect(tetris, tetris_field.field[y][x], (CUBE_SIDE*x, CUBE_SIDE*y, CUBE_SIDE,CUBE_SIDE), 0)
            pygame.draw.rect(tetris, GREED, (CUBE_SIDE*x, CUBE_SIDE*y, CUBE_SIDE, CUBE_SIDE), 1)
    for y in range(len(next_fig.field)):#Отрисовываем квадраты следующей фигуры на ее области
        for x in range(len(next_fig.field[y])):
            pygame.draw.rect(next_figure, next_fig.field[y][x], (CUBE_SIDE*x, CUBE_SIDE*y, CUBE_SIDE, CUBE_SIDE), 0)
            pygame.draw.rect(next_figure, GREED, (CUBE_SIDE*x, CUBE_SIDE*y, CUBE_SIDE, CUBE_SIDE), 1)
    for y in range(len(swap_fig.field)):#Отрисовываем квадраты удерживаемой фигуры на ее области
        for x in range(len(swap_fig.field[y])):
            pygame.draw.rect(swap_figure, swap_fig.field[y][x], (CUBE_SIDE*x, CUBE_SIDE*y,CUBE_SIDE,CUBE_SIDE), 0)
            pygame.draw.rect(swap_figure, GREED, (CUBE_SIDE*x, CUBE_SIDE*y, CUBE_SIDE,CUBE_SIDE), 1)
            
    score_text = text_font.render('score:{: >3}'.format(int(score)),0,TEXT_COLOR)
    screen.blit(tetris, (5, 5))# Отрисовываем поле тетриса
    screen.blit(next_text, (tetris_len_x+10, 5))#Отрисовываем Надпись next
    screen.blit(next_figure, (tetris_len_x+10, 25))#Отрисовываем поле следующей фигуры
    screen.blit(swap_text, (tetris_len_x+10, 120))# Отрисовываем надпись hold
    screen.blit(swap_figure, (tetris_len_x+10, 140))# Отрисовываем поле удерживаемой фигуры
    pygame.draw.rect(screen, AIR_COLOR, [tetris_len_x+10, 240, 150, 40], 0)#Зарисовываем белым место отрисовки счета
    pygame.draw.rect(screen, BORDER_COLOR, [1, 1, 365, 605], 1)
    pygame.draw.rect(screen, BORDER_COLOR, [369, 25, 122, 91], 1)
    pygame.draw.rect(screen, BORDER_COLOR, [369, 140, 122, 91], 1)
    screen.blit(score_text, (tetris_len_x+10,240))#Отрисовываем надпись счета
    screen.blit(hint_text, (5, 605))
                             
    pygame.display.flip()


def reset_game():#Функция, начинающая новую игру
    global score, down_pressed
    new_game_sound.play()
    down_pressed = False
    score = 0
    tetris_field.reset()
    next_fig.update_figure()
    figure.update_figure()
    next_fig.update_figure()
    swap_fig.update_figure()


pygame.init()
pygame.display.set_caption('Tetris')
strip_line_sound = pygame.mixer.Sound('pop.wav')
swap_sound = pygame.mixer.Sound('warning.wav')
move_sound = pygame.mixer.Sound('buttonrollover.wav')
rot_sound = pygame.mixer.Sound('startup.wav')
over_sound = pygame.mixer.Sound('critical.wav')
new_game_sound = pygame.mixer.Sound('buttonclickrelease.wav')

try:
    with open('config.json') as file:
        from json import load
        conf_data = load(file)
    WINDOW_SIZE = conf_data['WINDOW_SIZE']
    CUBE_SIDE = conf_data['CUBE_SIZE'] # размер квадрата из которых состоит поле тетриса
    AIR_COLOR = conf_data['AIR_COLOR'] # Стандартный цвет пустого квадата
    BORDER_COLOR = conf_data['BORDER_COLOR']
    TEXT_COLOR = conf_data['TEXT_COLOR']
    GAME_SPEED = conf_data['GAME_SPEED']
    SCORE_ADDER = GAME_SPEED/1000
    DOWN_SPEED = GAME_SPEED/10
    GREED = TEXT_COLOR if conf_data['GRID_ON'] else AIR_COLOR
    FONT_FILE = conf_data['FONT_FILE']
    if not conf_data['SOUND_ON']:
        for sound in strip_line_sound,swap_sound,move_sound,rot_sound,over_sound,new_game_sound:
            sound.set_volume(0.0)
        
except Exception as err:
    with open('errors.txt', 'a') as err_file:
        err_file.write(str(err.args)+'\n')
    exit()
    
screen = pygame.display.set_mode(WINDOW_SIZE)# Основной экран, на котором рисуются поверхности и счет игрока
screen.fill(AIR_COLOR)
next_figure = pygame.Surface((CUBE_SIDE*4, CUBE_SIDE*3))#Поверхность, на которой рисуется следующая фигура
swap_figure = pygame.Surface((CUBE_SIDE*4, CUBE_SIDE*3))
text_font = pygame.font.Font(FONT_FILE, 24)
next_text = text_font.render('Next', 0, TEXT_COLOR)
swap_text = text_font.render('Hold', 0, TEXT_COLOR)
tetris_len_x,tetris_len_y = 360, 600#Размер поверхости тетриса в пикселах
t_cells_x = int(tetris_len_x/CUBE_SIDE)#Количество ячеек по x при заданной длине поля
t_cells_y = int(tetris_len_y/CUBE_SIDE)
tetris = pygame.Surface((tetris_len_x, tetris_len_y))#Поверхость на которой рисуется тетрис

random_figures = (
    [[5,1],[6,1],[6,0],[7,0]],
    [[6,1],[7,1],[5,0],[6,0]],
    [[5,1],[6,1],[7,1],[6,0]],
    [[6,0],[7,0],[6,1],[7,1]],
    [[5,0],[6,0],[7,0],[7,1]],
    [[5,0],[6,0],[7,0],[5,1]],
    [[5,0],[6,0],[7,0],[8,0]]
                  )

random_colors = (
    (120,180,0),(240,120,120),(180,0,0),(140,0,140),(0,140,140),
    (240,120,0),(0,0,200),(0,140,0),(190,190,0),(255,128,0)
                )

# Правила вращения для каждой фигуры. У каждой фигуры есть собсвенные этапы вращения, каждый этап содержит 4 кортежа - правила перемещения для каждого квадрата фигуры
# Правило перемещения это просто 2 числа, которые прибавляются к x и y соответственно.Не у всех фигур по 4 этапа, а у фигуры, представляющей
# собой квадрат, этап состоит из нолей,такую фигуру вращать бессмысленно
figure_rotate = (
    (((0,0),(0,0),(-1,0),(-1,2) ),((0,0),(0,0),(1,0),(1,-2))),
    (((0,0),(0,0),(1,2),(1,0)),((0,0),(0,0),(-1,-2),(-1,0))),
    (((1,-1),(0,0),(-1,1),(1,1)),((1,1),(0,0),(-1,-1),(-1,1)),((-1,1),(0,0),(1,-1),(-1,-1)),((-1,-1),(0,0),(1,1),(1,-1))),
    (((0,0),(0,0),(0,0),(0,0)),),
    (((1,-1),(0,0),(-1,1),(-2,0)),((1,1),(0,0),(-1,-1),(0,-2)),((-1,1),(0,0),(1,-1),(2,0)),((-1,-1),(0,0),(1,1),(0,2))),
    (((1,-1),(0,0),(-1,1),(0,-2)),((1,1),(0,0),(-1,-1),(2,0)),((-1,1),(0,0),(1,-1),(0,2)),((-1,-1),(0,0),(1,1),(-2,0))),
    (((1,-1),(0,0),(-1,1),(-2,2)),((-1,1),(0,0),(1,-1),(2,-2)))
                )

tetris_field = Field(AIR_COLOR)
#Выбор случайной фигуры и случайного цвета из списков выше
figure = Figure(deepcopy(choice(random_figures)),choice(random_colors))# используем deepcopy так как нужна полная копия массива, а не еще одна ссылка на него
tetris_field.change_color(figure.rects_coords,figure.color)
next_fig = Next_fig(deepcopy(choice(random_figures)),choice(random_colors))
next_fig.change_color(next_fig.printed_figure, next_fig.color)
swap_fig = Swap_fig()
swap_fig.change_color(swap_fig.printed_figure,swap_fig.color)
game_alive, down_pressed, lost = True, False, False
score, speed, need_to_fall = 0, 1, 0
background = pygame.Surface(WINDOW_SIZE)
background.fill(AIR_COLOR)
background.set_alpha(5)
lose_font = pygame.font.Font(FONT_FILE, 50)
lose_text = lose_font.render('YOU LOSE', 0, TEXT_COLOR)
hint_font = pygame.font.Font(FONT_FILE, 14)
hint_text = hint_font.render('right/left-move up-rotate down-boost r_ctrl-swap figure r-restart', 0, TEXT_COLOR)
while game_alive:
    if not lost:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_alive = False
            keys = pygame.key.get_pressed()
            if event.type == pygame.KEYDOWN:
                if keys[pygame.K_DOWN]:
                    down_pressed = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    figure.move(1)
                elif event.key == pygame.K_LEFT:
                    figure.move(-1)
                elif event.key == pygame.K_UP:
                    figure.rotate()
                elif event.key == pygame.K_DOWN:
                    down_pressed = False
                elif event.key == pygame.K_RCTRL:
                    figure.swap()
                elif event.key == pygame.K_r:
                    reset_game()
        if down_pressed:# Если зажата стрелка вниз то перемещаем в 6 раз быстрее
            speed = DOWN_SPEED
            score += SCORE_ADDER
        else:
            speed = 1
        if need_to_fall > GAME_SPEED:
            if figure.get_collision() == None:#Если возвращает ноль, фигура не наложилась
                figure.fall()
                need_to_fall = 0
            else:
                lost = True
                over_sound.play()
        else:
            need_to_fall += speed
        animate()
    else:
        screen.blit(background, (0, 0))
        screen.blit(lose_text, (180, 180))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_alive = False
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_r:
                    lost = False
                    reset_game()
pygame.quit()
