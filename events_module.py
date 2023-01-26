import pygame

class Inpunting:
    is_key_left_pressed: bool = False
    is_key_up_pressed: bool = False
    is_key_down_pressed: bool = False
    is_key_right_pressed: bool = False
    is_key_null_pressed: bool = False
    is_key_enter_pressed: bool = False
    is_key_esc_pressed: bool = False
    is_key_w_pressed: bool = False
    is_key_s_pressed: bool = False
    is_key_a_pressed: bool = False
    is_key_d_pressed: bool = False

def get():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                Inpunting.is_key_left_pressed = True
                
            if event.key == pygame.K_RIGHT:
                Inpunting.is_key_right_pressed = True


            if event.key == pygame.K_DOWN:
                Inpunting.is_key_down_pressed = True


            if event.key == pygame.K_UP:
                Inpunting.is_key_up_pressed = True

            if event.key == pygame.K_w:
                Inpunting.is_key_w_pressed = True 

            if event.key == pygame.K_d:
                Inpunting.is_key_d_pressed = True

            if event.key == pygame.K_s:
                Inpunting.is_key_s_pressed = True

            if event.key == pygame.K_a:
                Inpunting.is_key_a_pressed = True       

            if event.key == pygame.K_RETURN:
                Inpunting.is_key_enter_pressed = True 

            if event.key == pygame.K_ESCAPE:
                Inpunting.is_key_esc_pressed = True

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                Inpunting.is_key_left_pressed = False

            if event.key == pygame.K_RIGHT:
                Inpunting.is_key_right_pressed = False

            if event.key == pygame.K_DOWN:
                Inpunting.is_key_down_pressed = False

            if event.key == pygame.K_UP:
                Inpunting.is_key_up_pressed = False 

            if event.key == pygame.K_w:
                Inpunting.is_key_w_pressed = False

            if event.key == pygame.K_d:
                Inpunting.is_key_d_pressed = False

            if event.key == pygame.K_s:
                Inpunting.is_key_s_pressed = False

            if event.key == pygame.K_a:
                Inpunting.is_key_a_pressed = False     

            if event.key == pygame.K_0:
                Inpunting.is_key_null_pressed = False

            if event.key == pygame.K_RETURN:
                Inpunting.is_key_enter_pressed = False 
                
            if event.key == pygame.K_ESCAPE:
                Inpunting.is_key_esc_pressed = False    