import Leap, sys, thread, time
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture
import socket
import json


TCP_IP = '127.0.0.1'
TCP_PORT = 5065
BUFFER_SIZE = 10000

class SampleListener(Leap.Listener):

    finger_names = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    bone_names = ['Metacarpal', 'Proximal', 'Intermediate', 'Distal']
    state_names = ['STATE_INVALID', 'STATE_START', 'STATE_UPDATE', 'STATE_END']
    swipe_direction=""
    dvec_x=0.0
    dvec_y=0.0
    dvec_z=0.0
    fingers_count=0
    
    def on_init(self, controller):
        print ("Leap Motion Initialized")
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((TCP_IP, TCP_PORT))
            print ("Connection established to Blender server")
        except:
            print ("connection error to Blender Server.Please check Port number")
            pass
        self.getnofingers(controller)
        print ("Swipe Up to activate the BlenderHMC server and Swipe Down to shutdown server")

    def on_connect(self, controller):
        # print ("Connected ")
        # Enable gestures
        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE);
        #controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP);
        #controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE);
        controller.config.set("Gesture.Swipe.MinLength", 150.0)
        controller.config.save()
    def on_disconnect(self, controller):
        print ("Disconnected")

    def on_exit(self, controller):
        print ("Exited")

    def on_frame(self, controller):
    	
        # Get the most recent frame and report some basic information
        frame = controller.frame()
        self.fingers_count=0

        # Get hands
        """
        for hand in frame.hands:

            handType = "Left hand" if hand.is_left else "Right hand"

            print " %s, id %d" % ( handType, hand.id, hand.palm_position)
        """
        #GetFinger
        fingers=frame.fingers.extended()
        for finger in fingers:
            #print (finger_names[finger.type])
            self.fingers_count=self.fingers_count+1    
        

        # Get gestures only with 2 or more fingers
        #print self.fingers_count
        if(self.fingers_count>=2):
            for gesture in frame.gestures():
                if gesture.type == Leap.Gesture.TYPE_CIRCLE:
                    circle = CircleGesture(gesture)

                    # Determine clock direction using the angle between the pointable and the circle normal
                    if circle.pointable.direction.angle_to(circle.normal) <= Leap.PI/2:
                        clockwiseness = "clockwise"
                    else:
                        clockwiseness = "counterclockwise"

                    # Calculate the angle swept since the last frame
                    swept_angle = 0
                    if circle.state != Leap.Gesture.STATE_START:
                        previous_update = CircleGesture(controller.frame(1).gesture(circle.id))
                        swept_angle =  (circle.progress - previous_update.progress) * 2 * Leap.PI

                    #print "  Circle id: %d, %s, progress: %f, radius: %f, angle: %f degrees, %s" % (
                            #gesture.id, self.state_names[gesture.state],
                            #circle.progress, circle.radius, swept_angle * Leap.RAD_TO_DEG, clockwiseness)

                if gesture.type == Leap.Gesture.TYPE_SWIPE:
                    swipe = SwipeGesture(gesture)
                    """
                    if(self.swipe_flag==1 or self.state_names[gesture.state]=="STATE_START"):
                    	if(self.state_names[gesture.state]=="STATE_START"):
                    		self.swipe_flag=1
                    """
                    dvec=swipe.direction
                    self.dvec_x=abs(dvec.x)
                    self.dvec_y=abs(dvec.y)
                    self.dvec_z=abs(dvec.z)
                    if(self.dvec_x>self.dvec_y and self.dvec_x>self.dvec_z):
                		if(dvec.x>0):
                			self.swipe_direction="Right"
                		else:
                			self.swipe_direction="Left"
                    if(self.dvec_y>self.dvec_x and self.dvec_y>self.dvec_z):
                		if(dvec.y>0):
                			self.swipe_direction="Up"
                		else:
                			self.swipe_direction="Down"
                    if(self.state_names[gesture.state]=="STATE_END"):
                		self.senddata (self.swipe_direction)

    def senddata(self,str1):
        #print str1
        try:
            message=str(str1)
            self.s.send(message.encode())
        except:
            print ("couldn't send")
            pass
    def getnofingers(self,controller):
    	#print "idhar hi me"
    	print "1:Add 2:Delete"
    	fingers_count=0
    	while fingers_count<=0:
    		frame=controller.frame()
    		fingers=frame.fingers.extended()
    		for finger in fingers:
    			fingers_count+=1
    		#print fingers_count
    	self.senddata(fingers_count)


def main():
    # Create a sample listener and controller
    listener = SampleListener()
    controller = Leap.Controller()
    
   # GetNoFingers(controller)
   # print "out"
    # Have the sample listener receive events from the controller
    controller.add_listener(listener)

    # Keep this process running until Enter is pressed
    print "Press Enter to quit..."
    try:
        sys.stdin.readline()
    except KeyboardInterrupt:
        pass
    finally:
        # Remove the sample listener when done
        controller.remove_listener(listener)


if __name__ == "__main__":
    main()