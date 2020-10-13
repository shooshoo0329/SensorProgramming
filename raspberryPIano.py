import pygame
import RPi.GPIO as GPIO
import time

# GPIO setting
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
gpio_pin = 13
GPIO.setup(gpio_pin, GPIO.OUT)
p = GPIO.PWM(gpio_pin, 100)

# print text on the screen
def printText(msg, pos):
    font = pygame.font.Font(None, 20)
    textSurface = font.render(msg, True, (255,255,255), None)
    textRect = textSurface.get_rect()
    textRect.topleft = pos
    screen.blit(textSurface, textRect)

# play scale when key pressed
def piano(p_num):
    scale = [261,294,329,349,392,440,493,523]
    p.start(100)
    p.ChangeDutyCycle(90)
    p.ChangeFrequency(scale[p_num])

# pygame setting
pygame.init()

size = [400, 300]
screen = pygame.display.set_mode(size)
screen.fill((0,0,0)) # black

pygame.display.set_caption("RASPBERRYPIano")

clock = pygame.time.Clock()
clock.tick(10)

# write guide on the screen
printText("Press Any Key!", (170, 50))
printText("Low DO : 'a' ~ High DO : 'k'", (130, 75))
printText("QUIT : ESC", (180, 100))

# main
try:
    run = True
    while run:
        for event in pygame.event.get(): # get the event
            if event.type == pygame.KEYDOWN: # when key pressed (only down)
                if event.key == pygame.K_ESCAPE: # press ESC to quit
                    run = False
                elif event.key == pygame.K_a: # Low DO
                    piano(0)
                elif event.key == pygame.K_s: # RE
                    piano(1)
                elif event.key == pygame.K_d: # MI
                    piano(2)
                elif event.key == pygame.K_f: # FA
                    piano(3)
                elif event.key == pygame.K_g: # SOL
                    piano(4)
                elif event.key == pygame.K_h: # LA
                    piano(5)
                elif event.key == pygame.K_j: # SI
                    piano(6)
                elif event.key == pygame.K_k: # High DO
                    piano(7)

            if event.type == pygame.KEYUP: # when key up (only up)
                p.ChangeDutyCycle(0) # mute

        pygame.display.flip() # needed to write text on the screen

# clean everything
finally:
    p.stop()
    pygame.quit()
    GPIO.cleanup()