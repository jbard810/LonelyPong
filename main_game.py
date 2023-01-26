import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import random as rnd
import math
import json
import csv
import os

'''
Resolution:
- Width: 1280
- Height: 720
Images: 
- Pause Button: https://icons8.com/icons/set/pause
'''


class Constants:
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    PADDLE_WIDTH = 0.2 * SCREEN_WIDTH
    PADDLE_HEIGHT = 20
    PADDLE_LIFT = 30
    PADDLE_SPEED = 27
    BALL_RADIUS = 10
    BALL_SPEED = 13
    BALL_COLOR = '#ffffff'


def new_init_game():
    # Paddle initialization
    px1 = 0.5 * (Constants.SCREEN_WIDTH - Constants.PADDLE_WIDTH)
    py1 = Constants.SCREEN_HEIGHT - (Constants.PADDLE_HEIGHT + Constants.PADDLE_LIFT)
    px2 = 0.5 * (Constants.SCREEN_WIDTH + Constants.PADDLE_WIDTH)
    py2 = Constants.SCREEN_HEIGHT - Constants.PADDLE_LIFT

    paddle_coords = [px1, py1, px2, py2]

    # Ball initialization

    x_mid = Constants.SCREEN_WIDTH / 2
    x_mid += rnd.uniform(-1 * (9 / 10) * x_mid, (9 / 10) * x_mid)
    y_mid = Constants.SCREEN_HEIGHT / 2 - 100

    theta = rnd.uniform(30, 165)

    bx1 = x_mid + Constants.BALL_RADIUS
    bx2 = x_mid - Constants.BALL_RADIUS
    by1 = y_mid + Constants.BALL_RADIUS
    by2 = y_mid - Constants.BALL_RADIUS

    ball_coords = [bx1, by1, bx2, by2]

    bv_x = Constants.BALL_SPEED * math.cos(math.radians(theta))
    bv_y = Constants.BALL_SPEED * math.sin(math.radians(theta))

    ball_speeds = [bv_x, bv_y]

    game_dict = {'player_name': '',
                 'color': 'green',
                 'paddle_coords': paddle_coords,
                 'ball_coords': ball_coords,
                 'ball_speeds': ball_speeds,
                 'score': 0,
                 'game_over': False}

    return game_dict


global game_dictionary, json_file

if not os.path.isfile('Game_State.json'):
    json_file = open('Game_State.json', 'w+')
else:
    json_file = open('Game_State.json', 'r')

json_string = json_file.read()

if len(json_string) == 0:
    game_dictionary = new_init_game()
    dict_list = [game_dictionary]
    dict_string_save = json.dumps(dict_list)
    json_file_save = open('Game_State.json', 'w')
    json_file_save.write(dict_string_save)
    json_file_save.close()
else:
    json_data = json.loads(json_string)
    game_dictionary = json_data[0]

json_file.close()


class Paddle:
    def __init__(self, canvas, master):
        self.master = master
        self.canvas = canvas
        self.x = 0
        self.y = 0
        self.paddle_velocity = Constants.PADDLE_SPEED

        # initial paddle creation
        [x1, y1, x2, y2] = game_dictionary['paddle_coords']
        self.rectangle = canvas.create_rectangle(x1, y1, x2, y2, outline='white', width=1,
                                                 fill=game_dictionary['color'])

        # displaying the paddle
        self.canvas.pack()

        # key bindings
        self.master.bind('<KeyPress-Left>', lambda e: self.left(e))
        self.master.bind('<KeyPress-Right>', lambda e: self.right(e))
        self.master.bind('<KeyRelease-Right>', lambda e: self.right_movement_release(e))
        self.master.bind('<KeyRelease-Left>', lambda e: self.left_movement_release(e))

        # updating the paddle movement
        self.movement()

    def left(self, event):
        self.x = -1 * Constants.PADDLE_SPEED
        self.y = 0
        self.paddle_velocity = -1 * Constants.PADDLE_SPEED

    def right(self, event):
        self.x = Constants.PADDLE_SPEED
        self.y = 0
        self.paddle_velocity = self.x

    def left_movement_release(self, event):
        self.x = -1 * Constants.PADDLE_SPEED / 7
        self.y = 0
        self.paddle_velocity = self.x

    def right_movement_release(self, event):
        self.x = Constants.PADDLE_SPEED / 7
        self.y = 0
        self.paddle_velocity = self.x

    def check_left_wall_collision(self):
        coordinates = self.canvas.coords(self.rectangle)
        if len(coordinates) != 0:
            x1 = coordinates[0]
            return x1 <= 0
        else:
            return False

    def check_right_wall_collision(self):
        coordinates = self.canvas.coords(self.rectangle)
        if len(coordinates) != 0:
            x2 = coordinates[2]
            return x2 >= Constants.SCREEN_WIDTH
        else:
            return False

    def movement(self):
        # paddle collision detection
        if self.check_left_wall_collision():
            self.master.unbind('<KeyPress-Left>')
            self.canvas.move(self.rectangle, self.x + 10, self.y)
        else:
            self.master.bind('<KeyPress-Left>', lambda e: self.left(e))
        if self.check_right_wall_collision():
            self.master.unbind('<KeyPress-Right>')
            self.canvas.move(self.rectangle, self.x - 10, self.y)
        else:
            self.master.bind('<KeyPress-Right>', lambda e: self.right(e))
        self.canvas.move(self.rectangle, self.x, self.y)
        self.canvas.after(20, self.movement)

        if len(self.canvas.coords(self.rectangle)) != 0:
            game_dictionary['paddle_coords'] = self.canvas.coords(self.rectangle)


class Ball:
    def __init__(self, canvas, paddle, master):
        self.master = master
        self.canvas = canvas
        self.paddle = paddle

        # ball creation
        [x1, y1, x2, y2] = game_dictionary['ball_coords']
        [self.v_x, self.v_y] = game_dictionary['ball_speeds']
        self.circle = self.canvas.create_oval(x1, y1, x2, y2, fill=Constants.BALL_COLOR)

        # score label creation
        self.score_var = tk.StringVar()
        self.score_var.set('Score: ' + str(game_dictionary['score']))
        self.score_label = tk.Label(self.canvas, textvariable=self.score_var, font='Helvetica, 20', bg='grey')
        self.score_label.place(x=(1 / 10) * Constants.SCREEN_WIDTH, y=34)

        self.pause_img = Image.open(r'assets\button_pause.png')
        self.resized_img = self.pause_img.resize((65, 65), Image.Resampling.LANCZOS)
        self.pause_img = ImageTk.PhotoImage(self.resized_img)
        self.pause_button = tk.Button(self.canvas, text='Pause Game', image=self.pause_img, command=self.pause_game)
        self.pause_button.place(x=(8/10) * Constants.SCREEN_WIDTH, y=30)

        # boss key (ctrl+b)
        self.master.bind('<Control-b>', lambda e: self.boss_key(e))

        # ball speed cheat code (ctrl+down)
        self.master.bind('<Control-Down>', lambda e: self.ball_speed_cheat_code(e))

        # point increase cheat code (ctrl+s)
        self.master.bind('<Control-s>', lambda e: self.point_increase_cheat_code(e))

        self.canvas.pack()

        self.movement()

    def pause_game(self):
        game_dictionary['paddle_coords'] = self.canvas.coords(self.paddle.rectangle)
        game_dictionary['ball_coords'] = self.canvas.coords(self.circle)
        self.canvas.delete('all')
        self.score_label.destroy()
        self.pause_button.destroy()
        self.canvas.destroy()
        PauseMenu(self.master)

    def boss_key(self, event):
        game_dictionary['paddle_coords'] = self.canvas.coords(self.paddle.rectangle)
        game_dictionary['ball_coords'] = self.canvas.coords(self.circle)
        self.canvas.delete('all')
        self.score_label.destroy()
        self.pause_button.destroy()
        BossKey(self.canvas, self.master)

    def ball_speed_cheat_code(self, event):
        # makes the magnitude of the velocity vector decrease by a factor of 10 %
        self.v_x *= 0.9
        self.v_y *= 0.9
        game_dictionary['ball_speeds'][0] = self.v_x
        game_dictionary['ball_speeds'][1] = self.v_y

    def point_increase_cheat_code(self, event):
        game_dictionary['score'] += 1
        self.score_var.set('Score: ' + str(game_dictionary['score']))
        self.master.update_idletasks()

    def check_left_wall_collision(self):
        coordinates = self.canvas.coords(self.circle)
        if len(coordinates) != 0:
            x1 = coordinates[0]
            return x1 <= Constants.BALL_RADIUS / 2
        else:
            return False

    def check_top_wall_collision(self):
        coordinates = self.canvas.coords(self.circle)
        if len(coordinates) != 0:
            y1 = coordinates[1]
            return y1 <= Constants.BALL_RADIUS / 2
        else:
            return False

    def check_right_wall_collision(self):
        coordinates = self.canvas.coords(self.circle)
        if len(coordinates) != 0:
            x2 = coordinates[2]
            return x2 >= Constants.SCREEN_WIDTH - Constants.BALL_RADIUS / 2
        else:
            return False

    def check_bottom_wall_collision(self):
        coordinates = self.canvas.coords(self.circle)
        buffer = 10  # a corrective buffer bc of frame rate
        if len(coordinates) != 0:
            y2 = coordinates[3]
            return y2 > Constants.SCREEN_HEIGHT - Constants.PADDLE_LIFT + buffer
        else:
            return False

    def check_paddle_collision(self):
        paddle_coordinates = self.canvas.coords(self.paddle.rectangle)
        ball_coordinates = self.canvas.coords(self.circle)
        buffer = 10

        paddle_x1 = paddle_coordinates[0]
        paddle_y1 = paddle_coordinates[1]
        paddle_x2 = paddle_coordinates[2]

        ball_x1 = ball_coordinates[0]
        ball_x2 = ball_coordinates[2]
        ball_y2 = ball_coordinates[3]

        return (ball_y2 - buffer > paddle_y1) and ((paddle_x1 <= ball_x1 <= paddle_x2)
                                                   and (paddle_x1 <= ball_x2 <= paddle_x2))

    def movement(self):
        # game object coordinates
        paddle_coords = self.canvas.coords(self.paddle.rectangle)
        ball_coords = self.canvas.coords(self.circle)

        # collision flags
        left_collision = self.check_left_wall_collision()
        right_collision = self.check_right_wall_collision()
        top_collision = self.check_top_wall_collision()
        bottom_collision = self.check_bottom_wall_collision()  #
        paddle_collision = False  # initialize to false so that the variable is in the proper scope
        if len(paddle_coords) != 0:
            paddle_collision = self.check_paddle_collision()

        # collision logic
        if bottom_collision:
            self.canvas.delete('all')
            self.score_label.destroy()
            self.pause_button.destroy()
            self.canvas.destroy()
            GameOver(self.master)
            game_dictionary['game_over'] = True
            return
        if left_collision or right_collision:
            self.v_x *= -1
            game_dictionary['ball_speeds'][0] = self.v_x
        if top_collision:
            self.v_y *= -1
            game_dictionary['ball_speeds'][1] = self.v_y
        if paddle_collision and len(ball_coords) != 0 and len(paddle_coords) != 0:
            speed_inc_factor = 1.005
            back_spin_constant = 1e-1
            self.v_y *= -1 * speed_inc_factor
            self.v_x *= speed_inc_factor
            self.v_x += speed_inc_factor + back_spin_constant * self.paddle.paddle_velocity
            game_dictionary['ball_speeds'][1] = self.v_y
            game_dictionary['ball_speeds'][0] = self.v_x
            game_dictionary['score'] += 1
            self.score_var.set('Score: ' + str(game_dictionary['score']))
        # canvas updates
        self.canvas.move(self.circle, self.v_x, self.v_y)
        self.canvas.after(20, self.movement)


class StartMenu:
    def __init__(self, canvas, master):
        self.canvas = canvas
        self.master = master

        self.main_title = tk.Label(self.canvas, text='Lonely Pong', font='Helvetica, 40', bg='grey', borderwidth=0)
        self.main_title.pack(side=tk.TOP, padx=50, pady=50)

        self.start_game_button = tk.Button(self.canvas, text='New Game', font='Helvetica, 20', bg='white',
                                           borderwidth=0, command=self.start_game)
        self.start_game_button.place(x=Constants.SCREEN_WIDTH / 2, y=(5 / 10) * Constants.SCREEN_HEIGHT)
        self.start_game_button.pack(padx=10, pady=10)

        self.load_game_button = tk.Button(self.canvas, text='Load Game', font='Helvetica, 20', bg='white',
                                          borderwidth=0, command=self.load_game)
        if game_dictionary['player_name'] == '':
            self.load_game_button['state'] = 'disabled'
        self.load_game_button.place(x=Constants.SCREEN_WIDTH / 2, y=(6 / 10) * Constants.SCREEN_HEIGHT)
        self.load_game_button.pack(padx=10, pady=10)

        self.exit_game_button = tk.Button(self.canvas, text='Exit Game', font='Helvetica, 20', bg='white',
                                          borderwidth=0, command=self.exit_game)
        self.exit_game_button.place(x=Constants.SCREEN_WIDTH / 2, y=(8 / 10) * Constants.SCREEN_HEIGHT)
        self.exit_game_button.pack(padx=10, pady=10)

        self.load_leaderboard_button = tk.Button(self.canvas, text='View Leaderboard', font='Helvetica, 20',
                                                 bg='white', borderwidth=0, command=self.load_leaderboard)
        self.load_leaderboard_button.place(x=Constants.SCREEN_WIDTH / 2, y=(7 / 10) * Constants.SCREEN_HEIGHT)
        self.load_leaderboard_button.pack(side=tk.BOTTOM, padx=10, pady=10)

        self.canvas.pack()

    def start_game(self):
        self.main_title.destroy()
        self.start_game_button.destroy()
        self.load_game_button.destroy()
        self.load_leaderboard_button.destroy()
        self.exit_game_button.destroy()
        self.canvas.delete('all')
        # checks to see if a save has already been made
        NewGameScreen(self.canvas, self.master)

    def load_game(self):
        self.main_title.destroy()
        self.start_game_button.destroy()
        self.load_game_button.destroy()
        self.load_leaderboard_button.destroy()
        self.exit_game_button.destroy()
        self.canvas.destroy()
        Game(self.master)

    def load_leaderboard(self):
        self.main_title.destroy()
        self.start_game_button.destroy()
        self.load_game_button.destroy()
        self.load_leaderboard_button.destroy()
        self.exit_game_button.destroy()
        self.canvas.destroy()
        LeaderBoard(self.master)

    def exit_game(self):
        self.canvas.destroy()
        self.master.destroy()


class LeaderBoard:
    def __init__(self, master):
        self.master = master
        self.canvas = tk.Canvas(self.master, width=Constants.SCREEN_WIDTH, height=Constants.SCREEN_HEIGHT, bd=0,
                                highlightthickness=0, relief='ridge', bg='grey')
        self.leaderboard_length = 10

        self.title_label = tk.Label(self.canvas, text='Leaderboard', font='Helvetica, 40', bg='grey', fg='black',
                                    anchor='center', borderwidth=0)
        self.title_label.place()

        self.start_menu_button = tk.Button(self.canvas, text='Return to Start Menu', font='Helvetica, 20',
                                           command=self.return_to_menu)
        self.start_menu_button.place()

        self.exit_button = tk.Button(self.canvas, text='Exit Game', font='Helvetica, 20', command=self.exit_game)
        self.exit_button.place(x=Constants.SCREEN_WIDTH / 2, y=(7 / 10) * Constants.SCREEN_HEIGHT)

        self.leaderboard = ttk.Treeview(self.canvas, columns=['1', '2', '3'], show='headings',
                                        height=self.leaderboard_length)
        self.leaderboard.place(x=Constants.SCREEN_WIDTH / 2, y=(3 / 10) * Constants.SCREEN_HEIGHT)
        self.leaderboard.heading(1, text='Ranking')
        self.leaderboard.heading(2, text='Player Name')
        self.leaderboard.heading(3, text='Score')

        self.max_entries = self.filter_data()

        self.insert_data(self.max_entries)

        self.style = ttk.Style()
        self.style.theme_use("default")
        self.style.map("Treeview")

        self.title_label.pack(side=tk.TOP, padx=50, pady=50)
        self.leaderboard.pack()
        self.start_menu_button.pack(padx=10, pady=10)
        self.exit_button.pack(side=tk.BOTTOM, padx=10, pady=10)

        self.canvas.pack()

    def exit_game(self):
        self.canvas.destroy()
        self.master.destroy()

    def return_to_menu(self):
        self.canvas.destroy()
        new_canvas = tk.Canvas(self.master, width=Constants.SCREEN_WIDTH, height=Constants.SCREEN_HEIGHT, bd=0,
                               highlightthickness=0, relief='ridge', bg='grey')
        StartMenu(new_canvas, self.master)

    def filter_data(self):
        data = []
        scores = []
        with open('leader_board.csv', newline='') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                data_entry = (row['player_name'], int(row['score']))  # tuple of each pair of data
                data.append(data_entry)
                scores.append(row['score'])
        sorted_data = sorted(data, key=lambda player: player[1])
        # check to see if there are too few entries to entirely populate the leaderboard
        if len(sorted_data) > self.leaderboard_length:
            last_entry_idx = len(sorted_data) - (self.leaderboard_length - 1)
            sorted_data = sorted[last_entry_idx:]

        ranked_data = []
        rank_idx = min(self.leaderboard_length, len(sorted_data))  # take the minimum in case there are too few entries
        for data in sorted_data:
            data_entry = (rank_idx, data[0], data[1])
            ranked_data.append(data_entry)
            rank_idx -= 1

        ranked_data.reverse()  # reverse bc it is going least to greatest

        return ranked_data

    def insert_data(self, filtered_data):
        data_idx = 0
        for data in filtered_data:
            row = (data[0], data[1], data[2])
            self.leaderboard.insert(parent='', index='end', iid=str(data_idx), text='', values=row)
            data_idx += 1


class NewGameScreen:
    def __init__(self, canvas, master):
        self.canvas = canvas
        self.master = master

        self.title_label = tk.Label(self.canvas, text='New Game Selection ', font='Helvetica, 40', bg='grey',
                                    fg='black', anchor='center', borderwidth=0)
        self.title_label.place(x=Constants.SCREEN_WIDTH / 2, y=(4 / 10) * Constants.SCREEN_HEIGHT)
        self.title_label.pack(side=tk.TOP, padx=30, pady=50)

        self.name_entry_label = tk.Label(self.canvas, text='Enter your name below: ', font='Helvetica, 20', bg='grey',
                                         anchor='center', borderwidth=0)
        self.name_entry_label.pack(padx=5, pady=5)

        self.name_entry = tk.Entry(self.canvas, width=40, font='Helvetica, 10')
        self.name_entry.place(x=Constants.SCREEN_WIDTH / 2, y=(3 / 10) * Constants.SCREEN_HEIGHT)
        self.name_entry.pack(padx=20, pady=20)

        self.color_entry_label = tk.Label(self.canvas, text='Choose a paddle color: ', font='Helvetica, 20', bg='grey',
                                          anchor='center', borderwidth=0)
        self.color_entry_label.pack(padx=5, pady=5)

        color_options = ['Green', 'Blue', 'Red']
        self.color_variable = tk.StringVar()
        self.color_variable.set(color_options[0])
        self.color_option_menu = tk.OptionMenu(self.canvas, self.color_variable, *color_options)
        self.color_option_menu.place(x=Constants.SCREEN_WIDTH / 2, y=(5 / 10) * Constants.SCREEN_HEIGHT)
        self.color_option_menu.pack(padx=30, pady=30)

        self.start_game_label = tk.Label(self.canvas, text='Choose an option to start the game: ', font='Helvetica, 20',
                                         bg='grey',
                                         anchor='center', borderwidth=0)
        self.start_game_label.pack(padx=5, pady=5)

        self.start_intro_button = tk.Button(self.canvas, text='Start Introduction', font='Helvetica, 20',
                                            command=self.start_intro)
        self.start_intro_button.place(x=Constants.SCREEN_WIDTH / 2, y=(4 / 10) * Constants.SCREEN_HEIGHT)
        self.start_intro_button.pack(padx=10, pady=10)

        self.start_game_button = tk.Button(self.canvas, text='Start Game', font='Helvetica, 20',
                                           command=self.start_game)
        self.start_game_button.place(x=Constants.SCREEN_WIDTH / 2, y=(4 / 10) * Constants.SCREEN_HEIGHT)
        self.start_game_button.pack(padx=10, pady=10)

        self.canvas.pack()

    def start_game(self):
        game_dictionary['player_name'] = self.name_entry.get()
        if game_dictionary['player_name'] == '':
            game_dictionary['player_name'] = ' '

        game_dictionary['color'] = self.color_variable.get().lower()

        self.title_label.destroy()
        self.name_entry_label.destroy()
        self.name_entry.destroy()
        self.start_game_label.destroy()
        self.start_game_button.destroy()
        self.start_intro_button.destroy()
        self.color_entry_label.destroy()
        self.color_option_menu.destroy()
        self.canvas.destroy()
        Game(self.master)

    def start_intro(self):
        game_dictionary['player_name'] = self.name_entry.get()
        if game_dictionary['player_name'] == '':
            game_dictionary['player_name'] = ' '

        game_dictionary['color'] = self.color_variable.get().lower()

        self.title_label.destroy()
        self.name_entry_label.destroy()
        self.name_entry.destroy()
        self.start_game_label.destroy()
        self.start_game_button.destroy()
        self.start_intro_button.destroy()
        self.color_entry_label.destroy()
        self.color_option_menu.destroy()
        Introduction(self.canvas, self.master)


class Introduction:
    def __init__(self, canvas, master):
        self.canvas = canvas
        self.master = master

        self.title_label = tk.Label(self.canvas, text='Introduction', font='Helvetica, 40', bg='grey',
                                    fg='black', anchor='center', borderwidth=0)
        self.title_label.place(x=Constants.SCREEN_WIDTH / 2, y=(4 / 10) * Constants.SCREEN_HEIGHT)
        self.title_label.pack(side=tk.TOP, padx=30, pady=50)

        with open('introduction.txt', 'r') as intro_file:
            introduction_paragraph = intro_file.read()

        self.intro_text = tk.Text(self.canvas, height=17, width=100, wrap=tk.WORD, bg='grey')
        self.intro_text.insert(tk.END, introduction_paragraph)
        self.intro_text.pack(padx=20, pady=20)

        self.start_game_button = tk.Button(self.canvas, text='Start Game', font='Helvetica, 20',
                                           command=self.start_game)
        self.start_game_button.place(x=Constants.SCREEN_WIDTH / 2, y=(4 / 10) * Constants.SCREEN_HEIGHT)
        self.start_game_button.pack(side=tk.BOTTOM, padx=30, pady=30)

    def start_game(self):
        self.title_label.destroy()
        self.intro_text.destroy()
        self.start_game_button.destroy()
        self.canvas.destroy()
        Game(self.master)


class PauseMenu:
    def __init__(self, master):
        self.master = master
        self.canvas = tk.Canvas(master, width=Constants.SCREEN_WIDTH, height=Constants.SCREEN_HEIGHT, bd=0,
                                highlightthickness=0, relief='ridge', bg='grey')

        self.title_label = tk.Label(self.canvas, text='Pause Menu', font='Helvetica, 40', bg='grey',
                                    fg='black', anchor='center', borderwidth=0)
        self.title_label.place(x=Constants.SCREEN_WIDTH / 2, y=(4 / 10) * Constants.SCREEN_HEIGHT)
        self.title_label.pack(side=tk.TOP, padx=30, pady=50)

        self.resume_game_button = tk.Button(self.canvas, text='Resume Game', font='Helvetica, 20',
                                            command=self.resume_game)
        self.resume_game_button.place(x=Constants.SCREEN_WIDTH / 2, y=(1 / 10) * Constants.SCREEN_HEIGHT)
        self.resume_game_button.pack(padx=10, pady=10)

        self.restart_game_button = tk.Button(self.canvas, text='Restart Game', font='Helvetica, 20',
                                             command=self.restart_game)
        self.restart_game_button.place(x=Constants.SCREEN_WIDTH / 2, y=(3 / 10) * Constants.SCREEN_HEIGHT)
        self.restart_game_button.pack(padx=10, pady=10)

        self.exit_game_button_save = tk.Button(self.canvas, text='Exit Game and Save', font='Helvetica, 20',
                                               command=self.exit_game_save)
        self.exit_game_button_save.place(x=Constants.SCREEN_WIDTH / 2, y=(5 / 10) * Constants.SCREEN_HEIGHT)
        self.exit_game_button_save.pack(padx=10, pady=10)

        self.exit_game_button = tk.Button(self.canvas, text='Exit Game', font='Helvetica, 20', command=self.exit_game)
        self.exit_game_button.place(x=Constants.SCREEN_WIDTH / 2, y=(7 / 10) * Constants.SCREEN_HEIGHT)
        self.exit_game_button.pack(padx=10, pady=10)

        self.canvas.pack()

    def resume_game(self):
        self.canvas.destroy()
        Game(self.master)

    def restart_game(self):
        cur_player_name = game_dictionary['player_name']
        cur_color_paddle = game_dictionary['color']
        new_game_dictionary = new_init_game()
        for key in game_dictionary.keys():
            game_dictionary[key] = new_game_dictionary[key]
        game_dictionary['player_name'] = cur_player_name
        game_dictionary['color'] = cur_color_paddle
        self.canvas.destroy()
        Game(self.master)

    def exit_game_save(self):
        exit_dict_list = [game_dictionary]
        exit_dict_string_save = json.dumps(exit_dict_list)
        exit_json_file_save = open('Game_State.json', 'w')
        exit_json_file_save.write(exit_dict_string_save)
        exit_json_file_save.close()
        self.canvas.destroy()
        self.master.destroy()

    def exit_game(self):
        os.remove('Game_State.json')
        self.canvas.destroy()
        self.master.destroy()


class BossKey:
    def __init__(self, canvas, master):
        self.canvas = canvas
        self.master = master

        boss_key_files = [r'assets\boss_key1.png', r'assets\boss_key2.png', r'assets\boss_key3.png',
                          r'assets\boss_key4.png', r'assets\boss_key5.png']
        self.boss_key_img = Image.open(rnd.choice(boss_key_files))  # randomly selects one of the images to display
        self.resized_img = self.boss_key_img.resize((Constants.SCREEN_WIDTH, Constants.SCREEN_HEIGHT),
                                                    Image.Resampling.LANCZOS)
        self.boss_key_img = ImageTk.PhotoImage(self.resized_img)
        self.canvas.create_image(Constants.SCREEN_WIDTH / 2, Constants.SCREEN_HEIGHT / 2, image=self.boss_key_img)

        self.master.bind('<Control-b>', lambda e: self.resume_game(e))

    def resume_game(self, event):
        self.canvas.delete('all')
        self.canvas.destroy()
        Game(self.master)


class Game:
    def __init__(self, master):
        self.master = master
        self.canvas = tk.Canvas(root, width=Constants.SCREEN_WIDTH, height=Constants.SCREEN_HEIGHT, bg='grey')
        self.game()

    def game(self):
        paddle = Paddle(self.canvas, self.master)
        Ball(self.canvas, paddle, self.master)
        self.canvas.pack()


class GameOver:
    def __init__(self, master):
        self.master = master
        self.canvas = tk.Canvas(self.master, width=Constants.SCREEN_WIDTH, height=Constants.SCREEN_HEIGHT, bd=0,
                                highlightthickness=0, relief='ridge', bg='grey')

        self.label1 = tk.Label(self.canvas, text='Game Over', font='Helvetica, 40', bg='grey', fg='black',
                               anchor='center', borderwidth=0)
        self.label1.place(x=Constants.SCREEN_WIDTH / 2, y=Constants.SCREEN_HEIGHT / 10)
        self.label1.pack(side=tk.TOP, padx=30, pady=30)
        self.label2 = tk.Label(self.canvas, text='Final Score: ' + str(game_dictionary['score']), font='Helvetica, 20',
                               bg='grey', fg='black', anchor='center', borderwidth=0)
        self.label2.place(x=Constants.SCREEN_WIDTH / 2, y=2 * Constants.SCREEN_HEIGHT / 10)
        self.label2.pack(padx=20, pady=20)

        self.play_again_button = tk.Button(self.canvas, text='Play Again?', font='Helvetica, 20', command=self.play_again)
        self.play_again_button.pack(padx=20, pady=20)

        self.exit_button = tk.Button(self.canvas, text='Exit Game', font='Helvetica, 20', command=self.exit_button)
        self.exit_button.place(x=Constants.SCREEN_WIDTH / 2, y=3 * Constants.SCREEN_HEIGHT / 10)
        self.exit_button.pack(padx=20, pady=20)

        self.canvas.pack()

    def play_again(self):
        # update the leaderboard csv file
        player = game_dictionary['player_name']
        score = game_dictionary['score']
        if player != ' ':  # does not include players without a name
            with open('leader_board.csv', 'a') as csv_file:
                column_keys = ['player_name', 'score']
                writer = csv.DictWriter(csv_file, fieldnames=column_keys)
                writer.writerow({'player_name': player, 'score': score})
        # set up the next game state dictionary
        color = game_dictionary['color']
        new_game_dictionary = new_init_game()
        for key in game_dictionary.keys():
            game_dictionary[key] = new_game_dictionary[key]
        game_dictionary['player_name'] = player
        game_dictionary['color'] = color
        self.canvas.destroy()
        Game(self.master)

    def exit_button(self):
        player = game_dictionary['player_name']
        score = game_dictionary['score']
        # update the leaderboard csv file
        if player != ' ':
            with open('leader_board.csv', 'a') as csv_file:
                column_keys = ['player_name', 'score']
                writer = csv.DictWriter(csv_file, fieldnames=column_keys)
                writer.writerow({'player_name': player, 'score': score})
        os.remove('Game_State.json')
        self.canvas.destroy()
        self.master.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Lonely Pong')
    root.geometry('1280x720')
    root.configure(bg='grey')

    game_canvas = tk.Canvas(root, width=Constants.SCREEN_WIDTH, height=Constants.SCREEN_HEIGHT, bd=0,
                            highlightthickness=0, relief='ridge', bg='grey')

    StartMenu(game_canvas, root)
    root.mainloop()
