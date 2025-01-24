import pygame
import sys
import random
import google.generativeai as genai
import tkinter as tk
from tkinter import ttk
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Отключаем сообщения TensorFlow
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'  # Отключаем приветствие pygame

# Инициализация Gemini API
genai.configure(api_key="AIzaSyCa_grfZ2eYXvzWcPgfBMTB9qiNzjWDcrE")
model = genai.GenerativeModel('gemini-pro')

# Размеры игрового окна
GAME_WIDTH = 600
GAME_HEIGHT = 600
TILE_SIZE = 40

# Размеры лабиринта
MAZE_ROWS = 8
MAZE_COLS = 8
MAZE_WIDTH = MAZE_COLS * TILE_SIZE
MAZE_HEIGHT = MAZE_ROWS * TILE_SIZE
# Центрируем лабиринт
MAZE_START_X = (GAME_WIDTH - MAZE_WIDTH) // 2
MAZE_START_Y = (GAME_HEIGHT - MAZE_HEIGHT) // 2

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)

class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
        self.visited = False

    def draw(self, screen, x, y):
        # Рисуем пол с текстурой
        screen.blit(game.floor_image, (x, y))
        
        # Рисуем стены используя текстуру
        if self.walls['top']:
            screen.blit(game.wall_image, (x, y), (0, 0, TILE_SIZE, 5))
        if self.walls['right']:
            screen.blit(game.wall_image, (x + TILE_SIZE - 5, y), (0, 0, 5, TILE_SIZE))
        if self.walls['bottom']:
            screen.blit(game.wall_image, (x, y + TILE_SIZE - 5), (0, 0, TILE_SIZE, 5))
        if self.walls['left']:
            screen.blit(game.wall_image, (x, y), (0, 0, 5, TILE_SIZE))

class QuestionWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Питання")
        self.root.geometry("500x600")  # Увеличили высоту для сообщения об ошибке
        self.root.resizable(False, False)
        
        # Заголовок
        self.title_label = ttk.Label(self.root, text="Основи програмування", 
                                   font=('Arial', 16, 'bold'))
        self.title_label.pack(pady=20)
        
        # Область для вопроса
        self.question_frame = ttk.Frame(self.root)
        self.question_frame.pack(fill='x', padx=20, pady=10)
        
        self.question_label = ttk.Label(self.question_frame, wraplength=450, 
                                      font=('Arial', 12), justify='center')
        self.question_label.pack(pady=20)
        
        # Кнопки для ответов
        self.buttons_frame = ttk.Frame(self.root)
        self.buttons_frame.pack(pady=20)
        
        style = ttk.Style()
        style.configure('Answer.TButton', font=('Arial', 10), padding=10)
        
        self.answer_buttons = []
        for i in range(4):
            btn = ttk.Button(self.buttons_frame, style='Answer.TButton', width=40)
            btn.pack(pady=10)
            self.answer_buttons.append(btn)
            
        # Улучшаем область для сообщения об ошибке
        self.feedback_label = ttk.Label(
            self.root, 
            text="", 
            font=('Arial', 12, 'bold'),
            wraplength=400,  # Разрешаем перенос строк
            justify='center'
        )
        self.feedback_label.pack(pady=20)
        
        self.game = None
        self.current_question = None

    def set_game(self, game):
        self.game = game
        self.load_question()

    def load_backup_question(self):
        backup_question = {
            'question': 'Що таке змінна в програмуванні?',
            'options': {
                'А': 'Контейнер для зберігання даних',
                'Б': 'Тип даних',
                'В': 'Функція',
                'Г': 'Оператор'
            },
            'correct': 'А'
        }
        self.current_question = backup_question
        self.question_label.config(text=self.current_question['question'])
        
        for i, (key, value) in enumerate(self.current_question['options'].items()):
            self.answer_buttons[i].config(
                text=f"{key}: {value}",
                command=lambda k=key: self.check_answer(k)
            )

    def load_question(self):
        try:
            prompt = """
            Створи унікальне питання з програмування.
            Тема: Основи програмування
            
            Формат:
            ПИТАННЯ: [коротке питання]
            А: [варіант]
            Б: [варіант]
            В: [варіант]
            Г: [варіант]
            ПРАВИЛЬНА: [А/Б/В/Г]
            """
            
            response = model.generate_content(prompt, generation_config={
                'temperature': 0.9,  # Увеличиваем случайность
                'top_p': 0.9,
                'top_k': 40,
                'max_output_tokens': 200,
                'candidate_count': 1
            })
            
            lines = [line.strip() for line in response.text.split('\n') if line.strip()]
            
            filtered_lines = [
                line for line in lines 
                if any(line.startswith(prefix) for prefix in ['ПИТАННЯ:', 'А:', 'Б:', 'В:', 'Г:', 'ПРАВИЛЬНА:'])
            ][:6]
            
            if len(filtered_lines) != 6:
                raise ValueError()
                
            self.current_question = {
                'question': filtered_lines[0].replace('ПИТАННЯ:', '').strip(),
                'options': {
                    'А': filtered_lines[1].replace('А:', '').strip(),
                    'Б': filtered_lines[2].replace('Б:', '').strip(),
                    'В': filtered_lines[3].replace('В:', '').strip(),
                    'Г': filtered_lines[4].replace('Г:', '').strip()
                },
                'correct': filtered_lines[5].replace('ПРАВИЛЬНА:', '').strip()
            }
            
            self.update_question_display()
                
        except:
            self.load_backup_question()

    def update_question_display(self):
        """Обновляет отображение вопроса и вариантов ответов"""
        self.question_label.config(text=self.current_question['question'])
        self.feedback_label.config(text="")
        
        for i, (key, value) in enumerate(self.current_question['options'].items()):
            self.answer_buttons[i].config(
                text=f"{key}: {value}",
                command=lambda k=key: self.check_answer(k)
            )

    def check_answer(self, answer):
        if self.game and self.current_question:
            correct = self.current_question['correct']
            if answer == correct:
                self.feedback_label.config(
                    text="Правильно!",
                    foreground='green'
                )
                self.game.correct_answer()
            else:
                # Формируем подробное сообщение об ошибке
                wrong_answer = self.current_question['options'][answer]
                correct_answer = self.current_question['options'][correct]
                error_message = (
                    f"Неправильно!\n\n"
                    f"Ви обрали: {answer}) {wrong_answer}\n"
                    f"Правильна відповідь: {correct}) {correct_answer}"
                )
                
                self.feedback_label.config(
                    text=error_message,
                    foreground='red',
                    justify='center'
                )
                self.game.wrong_answer()
                # Даем время прочитать сообщение об ошибке
                self.root.after(3000, self.load_question)

    def update(self):
        try:
            self.root.update()
        except:
            pass

    def destroy(self):
        try:
            if self.root:
                self.root.quit()
                self.root.destroy()
        except:
            pass

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((GAME_WIDTH, GAME_HEIGHT))
        pygame.display.set_caption("Лабіринт")
        
        self.load_images()
        Cell.game = self
        self.reset_game_state()
        self.question_window = QuestionWindow()
        self.question_window.set_game(self)
    
    def load_images(self):
        try:
            self.wall_image = pygame.transform.scale(
                pygame.image.load('block.png'), 
                (TILE_SIZE, TILE_SIZE)
            )
            self.floor_image = pygame.transform.scale(
                pygame.image.load('floor.png'), 
                (TILE_SIZE, TILE_SIZE)
            )
            self.player_image = pygame.transform.scale(
                pygame.image.load('player.png'), 
                (TILE_SIZE - 10, TILE_SIZE - 10)
            )
            self.treasure_image = pygame.transform.scale(
                pygame.image.load('treasure.png'), 
                (TILE_SIZE - 10, TILE_SIZE - 10)
            )
            self.heart_image = pygame.transform.scale(
                pygame.image.load('heart.png'), 
                (30, 30)
            )
        except:
            # Создаем простые цветные прямоугольники вместо изображений
            self.create_fallback_images()

    def reset_game_state(self):
        """Сброс состояния игры"""
        self.maze = self.generate_maze()
        self.player_pos = [0, 0]
        self.treasure_pos = [MAZE_ROWS-1, MAZE_COLS-1]
        self.lives = 3
        self.score = 0
        self.moving_to_treasure = False
        self.path_to_treasure = []
        self.move_button_rect = None

    def generate_maze(self):
        # Создаем сетку
        grid = [[Cell(row, col) for col in range(MAZE_COLS)] for row in range(MAZE_ROWS)]
        
        def get_neighbors(cell):
            neighbors = []
            directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # top, right, bottom, left
            
            for dx, dy in directions:
                new_row, new_col = cell.row + dy, cell.col + dx
                if (0 <= new_row < MAZE_ROWS and 0 <= new_col < MAZE_COLS and 
                    not grid[new_row][new_col].visited):
                    neighbors.append((grid[new_row][new_col], dx, dy))
            return neighbors

        # Алгоритм генерации
        def carve_path(current):
            current.visited = True
            neighbors = get_neighbors(current)
            
            while neighbors:
                next_cell, dx, dy = random.choice(neighbors)
                if not next_cell.visited:
                    # Убираем стены между клетками
                    if dx == 1:  # right
                        current.walls['right'] = False
                        next_cell.walls['left'] = False
                    elif dx == -1:  # left
                        current.walls['left'] = False
                        next_cell.walls['right'] = False
                    elif dy == 1:  # bottom
                        current.walls['bottom'] = False
                        next_cell.walls['top'] = False
                    elif dy == -1:  # top
                        current.walls['top'] = False
                        next_cell.walls['bottom'] = False
                    
                    carve_path(next_cell)
                
                neighbors = get_neighbors(current)

        # Начинаем с верхней левой клетки
        start_cell = grid[0][0]
        carve_path(start_cell)
        
        return grid

    def find_path_to_treasure(self):
        # Поиск пути к сокровищу через BFS
        queue = [(self.player_pos, [])]
        visited = set()
        
        while queue:
            (current_pos, path) = queue.pop(0)
            row, col = current_pos
            
            if current_pos == self.treasure_pos:
                return path
                
            if tuple(current_pos) not in visited:
                visited.add(tuple(current_pos))
                
                # Проверяем все возможные направления
                directions = [
                    ('UP', [-1, 0]),
                    ('DOWN', [1, 0]),
                    ('LEFT', [0, -1]),
                    ('RIGHT', [0, 1])
                ]
                
                for direction, (dy, dx) in directions:
                    new_row, new_col = row + dy, col + dx
                    if (0 <= new_row < MAZE_ROWS and 0 <= new_col < MAZE_COLS):
                        cell = self.maze[row][col]
                        # Проверяем стены
                        if (direction == 'UP' and not cell.walls['top'] or
                            direction == 'DOWN' and not cell.walls['bottom'] or
                            direction == 'LEFT' and not cell.walls['left'] or
                            direction == 'RIGHT' and not cell.walls['right']):
                            queue.append(([new_row, new_col], path + [direction]))
        return []

    def correct_answer(self):
        self.score += 1
        self.path_to_treasure = self.find_path_to_treasure()
        if self.path_to_treasure:
            self.moving_to_treasure = True
            # Берем только один шаг из пути
            self.path_to_treasure = [self.path_to_treasure[0]]

    def wrong_answer(self):
        self.lives -= 1
        self.moving_to_treasure = False
        self.path_to_treasure = []
            
        # Визуальный эффект потери жизни (красная вспышка)
        original_surface = self.screen.copy()
        for alpha in range(0, 128, 32):  # Плавное появление и исчезновение
            self.screen.blit(original_surface, (0, 0))
            red_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
            red_surface.fill((255, 0, 0))
            red_surface.set_alpha(alpha)
            self.screen.blit(red_surface, (0, 0))
            pygame.display.flip()
            pygame.time.wait(20)
        
        # Возвращаем оригинальное изображение
        self.screen.blit(original_surface, (0, 0))
        pygame.display.flip()

    def show_intro(self):
        self.screen.fill((230, 230, 250))
        
        # Заголовок
        title_font = pygame.font.Font(None, 72)
        title = title_font.render('Лабіринт Знань', True, (47, 79, 79))
        title_rect = title.get_rect(center=(GAME_WIDTH//2, 80))
        
        # Добавляем подчеркивание для заголовка
        pygame.draw.line(self.screen, (47, 79, 79),
                        (title_rect.left, title_rect.bottom + 5),
                        (title_rect.right, title_rect.bottom + 5), 3)
        
        self.screen.blit(title, title_rect)
        
        # Подзаголовок
        subtitle_font = pygame.font.Font(None, 36)
        subtitle = subtitle_font.render('Освітня гра для вивчення програмування', True, (70, 130, 180))
        subtitle_rect = subtitle.get_rect(center=(GAME_WIDTH//2, 130))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Описание игры
        font = pygame.font.Font(None, 32)
        
        # Описание персонажа
        char_desc = "Допоможіть Баблу знайти скарб знань!"
        char_text = font.render(char_desc, True, (0, 0, 0))
        char_rect = char_text.get_rect(center=(GAME_WIDTH//2, 180))
        self.screen.blit(char_text, char_rect)
        
        # Правила
        rules_title = font.render("Правила гри:", True, (47, 79, 79))
        rules_rect = rules_title.get_rect(center=(GAME_WIDTH//2, 240))
        self.screen.blit(rules_title, rules_rect)
        
        rules = [
            "1. Відповідайте на питання з програмування",
            "2. За правильну відповідь Бабл робить крок",
            "3. За помилку втрачається одне життя",
            "4. Знайдіть скарб, щоб перемогти!"
        ]
        
        for i, rule in enumerate(rules):
            rule_text = font.render(rule, True, (0, 0, 0))
            rule_rect = rule_text.get_rect(center=(GAME_WIDTH//2, 280 + i * 35))
            self.screen.blit(rule_text, rule_rect)
        
        # Управление
        controls = [
            "R - Рестарт гри",
            "ESC - Вихід"
        ]
        
        controls_y = 440
        for control in controls:
            control_text = font.render(control, True, (70, 130, 180))
            control_rect = control_text.get_rect(center=(GAME_WIDTH//2, controls_y))
            self.screen.blit(control_text, control_rect)
            controls_y += 35
        
        # Кнопка "Почати"
        button_width = 200
        button_height = 50
        button_x = GAME_WIDTH//2 - button_width//2
        button_y = GAME_HEIGHT - 100
        
        self.start_button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
        
        # Рисуем кнопку с градиентом и тенью
        shadow_rect = self.start_button_rect.copy()
        shadow_rect.y += 3
        pygame.draw.rect(self.screen, (0, 0, 0, 128), shadow_rect, border_radius=15)
        pygame.draw.rect(self.screen, (152, 251, 152), self.start_button_rect, border_radius=15)
        
        # Текст кнопки
        button_text = font.render('Почати гру', True, (47, 79, 79))
        text_rect = button_text.get_rect(center=self.start_button_rect.center)
        self.screen.blit(button_text, text_rect)
        
        pygame.display.flip()
        
        # Ожидание действия игрока
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (
                    event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                ):
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Проверяем клик по кнопке
                    if self.start_button_rect.collidepoint(event.pos):
                        return
                elif event.type == pygame.MOUSEMOTION:
                    # Эффект при наведении
                    if self.start_button_rect.collidepoint(event.pos):
                        pygame.draw.rect(self.screen, (130, 230, 130), self.start_button_rect, border_radius=15)
                    else:
                        pygame.draw.rect(self.screen, (152, 251, 152), self.start_button_rect, border_radius=15)
                    # Обновляем текст кнопки
                    self.screen.blit(button_text, text_rect)
                    pygame.display.flip()

    def game_over(self):
        self.screen.fill((230, 230, 250))  # Светлый фон
        
        # Заголовок
        title_font = pygame.font.Font(None, 74)
        if self.player_pos == self.treasure_pos:
            title = title_font.render('Перемога!', True, (34, 139, 34))  # Зеленый
        else:
            title = title_font.render('Гра закінчена!', True, (178, 34, 34))  # Красный
            
        title_rect = title.get_rect(center=(GAME_WIDTH//2, GAME_HEIGHT//2 - 100))
        self.screen.blit(title, title_rect)
        
        # Счет
        font = pygame.font.Font(None, 48)
        score_text = font.render(f'Ваш рахунок: {self.score}', True, (47, 79, 79))
        score_rect = score_text.get_rect(center=(GAME_WIDTH//2, GAME_HEIGHT//2))
        self.screen.blit(score_text, score_rect)
        
        # Инструкции
        font = pygame.font.Font(None, 36)
        texts = [
            "Натисніть R для нової гри",
            "Натисніть ESC для виходу"
        ]
        
        for i, text in enumerate(texts):
            text_surface = font.render(text, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(GAME_WIDTH//2, GAME_HEIGHT//2 + 50 + i * 40))
            self.screen.blit(text_surface, text_rect)
        
        pygame.display.flip()
        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.question_window.destroy()
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # Рестарт по R
                        self.reset_game_state()
                        self.question_window.load_question()
                        waiting = False
                    elif event.key == pygame.K_ESCAPE:  # Выход по ESC
                        self.question_window.destroy()
                        pygame.quit()
                        sys.exit()

    def run(self):
        self.show_intro()
        
        clock = pygame.time.Clock()
        running = True
        self.auto_move_timer = 0
        
        while running:
            try:
                self.screen.fill((230, 230, 250))
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            running = False
                        elif event.key == pygame.K_r:  # Рестарт по R в любой момент
                            self.reset_game_state()
                            self.question_window.load_question()
                
                # Автоматическое движение
                if self.moving_to_treasure and self.path_to_treasure:
                    self.auto_move_timer += 1
                    if self.auto_move_timer >= 20:
                        self.auto_move_timer = 0
                        self.move_to_treasure()
                
                self.draw_maze()
                self.draw_player()
                self.draw_treasure()
                self.draw_hearts()
                
                if self.lives <= 0 or self.player_pos == self.treasure_pos:
                    self.game_over()
                    continue
                
                pygame.display.flip()
                self.question_window.update()
                clock.tick(60)
                
            except Exception:
                running = False
            
        self.question_window.destroy()
        pygame.quit()
        sys.exit()

    def move_to_treasure(self):
        if not self.path_to_treasure or not self.moving_to_treasure:
            return
            
        next_move = self.path_to_treasure.pop(0)
        self.move_player(next_move)
        
        if self.player_pos == self.treasure_pos:
            self.game_over()
            return
            
        # Загружаем новый вопрос только после завершения всего пути
        if not self.path_to_treasure:
            self.moving_to_treasure = False
            self.question_window.load_question()

    def draw_maze(self):
        # Рисуем фон лабиринта с текстурой
        for row in range(MAZE_ROWS):
            for col in range(MAZE_COLS):
                x = MAZE_START_X + col * TILE_SIZE
                y = MAZE_START_Y + row * TILE_SIZE
                # Сначала рисуем текстуру пола для всех клеток
                self.screen.blit(self.floor_image, (x, y))
                # Затем рисуем стены
                self.maze[row][col].draw(self.screen, x, y)

    def draw_player(self):
        x = MAZE_START_X + self.player_pos[1] * TILE_SIZE
        y = MAZE_START_Y + self.player_pos[0] * TILE_SIZE
        # Центрируем игрока в клетке
        self.screen.blit(self.player_image, 
                        (x + (TILE_SIZE - self.player_image.get_width())//2,
                         y + (TILE_SIZE - self.player_image.get_height())//2))

    def draw_treasure(self):
        x = MAZE_START_X + self.treasure_pos[1] * TILE_SIZE
        y = MAZE_START_Y + self.treasure_pos[0] * TILE_SIZE
        # Центрируем сокровище в клетке
        self.screen.blit(self.treasure_image, 
                        (x + (TILE_SIZE - self.treasure_image.get_width())//2,
                         y + (TILE_SIZE - self.treasure_image.get_height())//2))

    def draw_hearts(self):
        for i in range(self.lives):
            x = 30 + i * 40
            y = 30
            self.screen.blit(self.heart_image, (x - 15, y - 15))

    def move_player(self, direction):
        row, col = self.player_pos
        moved = False
        
        if direction == 'UP' and row > 0 and not self.maze[row][col].walls['top']:
            self.player_pos[0] -= 1
            moved = True
        elif direction == 'DOWN' and row < MAZE_ROWS-1 and not self.maze[row][col].walls['bottom']:
            self.player_pos[0] += 1
            moved = True
        elif direction == 'LEFT' and col > 0 and not self.maze[row][col].walls['left']:
            self.player_pos[1] -= 1
            moved = True
        elif direction == 'RIGHT' and col < MAZE_COLS-1 and not self.maze[row][col].walls['right']:
            self.player_pos[1] += 1
            moved = True
        
        # Убираем загрузку нового вопроса после каждого движения
        if moved:
            self.moving_to_treasure = False

if __name__ == "__main__":
    game = Game()
    game.run()
