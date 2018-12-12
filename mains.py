import pygame  
import random  

frames = 60

win_wd = 400
win_ht = 400
pd_wd = 10
pd_ht = 60
pd_bf = 10
ball_wd = 10
ball_ht = 10
pd_vel = 2
ball_x_vel = 3
ball_y_vel = 2

white = (255, 255, 255)
black = (0, 0, 0)

game_display = pygame.display.set_mode((win_wd, win_ht))


def draw_ball(ball_x_pos, ball_y_pos):
    ball = pygame.Rect(ball_x_pos, ball_y_pos, ball_wd, ball_ht)
    pygame.draw.rect(game_display, white, ball)


def draw_pd1(pd1_y_pos):
    pd1 = pygame.Rect(pd_bf, pd1_y_pos, pd_wd, pd_ht)
    pygame.draw.rect(game_display, white, pd1)


def draw_pd2(pd2_y_pos):
    pd2 = pygame.Rect(win_wd - pd_bf - pd_wd, pd2_y_pos, pd_wd, pd_ht)
    pygame.draw.rect(game_display, white, pd2)


def update_ball_pos(pd1_y_pos, pd2_y_pos, ball_x_pos, ball_y_pos, ball_x_dir, ball_y_dir):
    ball_x_pos = ball_x_pos + ball_x_dir * ball_x_vel
    ball_y_pos = ball_y_pos + ball_y_dir * ball_y_vel
    score = 0

    if ball_x_pos <= pd_bf + pd_wd and ball_y_pos + ball_ht >= pd1_y_pos and ball_y_pos - ball_ht <= pd1_y_pos + pd_ht:
        ball_x_dir = 1
    
    elif ball_x_pos <= 0:
        ball_x_dir = 1
        score = -1
        return [score, pd1_y_pos, pd2_y_pos, ball_x_pos, ball_y_pos, ball_x_dir, ball_y_dir]

    if ball_x_pos >= win_wd - pd_wd - pd_bf and ball_y_pos + ball_ht >= pd2_y_pos and ball_y_pos - ball_ht <= pd2_y_pos + pd_ht:
        ball_x_dir = -1
    
    elif ball_x_pos >= win_wd - ball_wd:
        ball_x_dir = -1
        score = 1
        return [score, pd1_y_pos, pd2_y_pos, ball_x_pos, ball_y_pos, ball_x_dir, ball_y_dir]

    if ball_y_pos <= 0:
        ball_y_pos = 0;
        ball_y_dir = 1;
    
    elif ball_y_pos >= win_ht - ball_ht:
        ball_y_pos = win_ht - ball_ht
        ball_y_dir = -1
    return [score, pd1_y_pos, pd2_y_pos, ball_x_pos, ball_y_pos, ball_x_dir, ball_y_dir]


def update_pd1(act, pd1_y_pos):
    
    if act[1] == 1:
        pd1_y_pos = pd1_y_pos - pd_vel
    
    if act[2] == 1:
        pd1_y_pos = pd1_y_pos + pd_vel
    
    if pd1_y_pos < 0:
        pd1_y_pos = 0

    if pd1_y_pos > win_ht - pd_ht:
        pd1_y_pos = win_ht - pd_ht
    return pd1_y_pos


def update_pd2(pd2_y_pos, ball_y_pos):
    
    if pd2_y_pos + pd_ht / 2 < ball_y_pos + ball_ht / 2:
        pd2_y_pos = pd2_y_pos + pd_vel
    
    if pd2_y_pos + pd_ht / 2 > ball_y_pos + ball_ht / 2:
        pd2_y_pos = pd2_y_pos - pd_vel
    
    if pd2_y_pos < 0:
        pd2_y_pos = 0
    
    if pd2_y_pos > win_ht - pd_ht:
        pd2_y_pos = win_ht - pd_ht
    return pd2_y_pos


class MainGame:
    def __init__(self):
        num = random.randint(0, 9)
        
        self.tally = 0
        
        self.pd1_y_pos = win_ht / 2 - pd_ht / 2
        self.pd2_y_pos = win_ht / 2 - pd_ht / 2
        
        self.ball_x_dir = 1
        self.ball_y_dir = 1
        
        self.ball_x_pos = win_wd / 2 - ball_wd / 2

        if 0 < num < 3:
            self.ball_x_dir = 1
            self.ball_y_dir = 1

        if 3 <= num < 5:
            self.ball_x_dir = -1
            self.ball_y_dir = 1

        if 5 <= num < 8:
            self.ball_x_dir = 1
            self.ball_y_dir = -1

        if 8 <= num < 10:
            self.ball_x_dir = -1
            self.ball_y_dir = -1
        
        num = random.randint(0, 9)
        
        self.ball_y_pos = num * (win_ht - ball_ht) / 9

    def curr_frame(self):
        pygame.event.pump()
        
        game_display.fill(black)
        
        draw_pd1(self.pd1_y_pos)
        draw_pd2(self.pd2_y_pos)
        
        draw_ball(self.ball_x_pos, self.ball_y_pos)
        
        image_data = pygame.surfarray.array3d(pygame.display.get_surface())
        
        pygame.display.flip()
        
        return image_data

    def next_frame(self, act):
        pygame.event.pump()
        score = 0
        game_display.fill(black)
        
        self.pd1_y_pos = update_pd1(act, self.pd1_y_pos)
        draw_pd1(self.pd1_y_pos)
        
        self.pd2_y_pos = update_pd2(self.pd2_y_pos, self.ball_y_pos)
        draw_pd2(self.pd2_y_pos)
        
        [score, self.pd1_y_pos, self.pd2_y_pos, self.ball_x_pos, self.ball_y_pos, self.ball_x_dir,
         self.ball_y_dir] = update_ball_pos(self.pd1_y_pos, self.pd2_y_pos, self.ball_x_pos, self.ball_y_pos,
                                            self.ball_x_dir, self.ball_y_dir)
        
        draw_ball(self.ball_x_pos, self.ball_y_pos)
        
        image_data = pygame.surfarray.array3d(pygame.display.get_surface())
        
        pygame.display.flip()
        
        self.tally = self.tally + score
        # print("Tally is " + str(self.tally))
        
        return [score, image_data]
