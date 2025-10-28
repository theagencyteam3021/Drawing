import Drawonplane
import tkinter

PAPER_SCALE = 50

paperSizeX = 8.5*PAPER_SCALE
paperSizeY = 11*PAPER_SCALE

window = tkinter.Tk()

window.configure(bg='black')

Drawonplane.home()
input()
Drawonplane.drawAbove(0,0)
Drawonplane.drawOn(0,0)
currentX = 0
currentY = 0

paperRect = tkinter.Canvas(window,width=paperSizeX,height=paperSizeY)

def onPaperClick(event):
    global currentX, currentY
    RobotTargetX = event.y/paperSizeX
    RobotTargetY = event.x/paperSizeY
    targetX = event.x/paperSizeX
    targetY = event.y/paperSizeY
    print(f"{RobotTargetX},{RobotTargetY}")
    paperRect.create_line(currentX*paperSizeX,currentY*paperSizeY,targetX*paperSizeX,targetY*paperSizeY,width=3,fill="black")
    Drawonplane.drawOn(RobotTargetX,RobotTargetY)
    currentX = targetX
    currentY = targetY
    
paperRect.bind("<Button-1>",onPaperClick)
paperRect.pack()

window.mainloop()