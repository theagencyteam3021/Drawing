# ur_robot.py
import socket
import time
from typing import List, Tuple, Union

# Define a type hint for pose or joint configurations
PoseOrJoints = Union[List[float], Tuple[float, ...]]

class UniversalRobot:
    """
    A class to control a Universal Robot (UR) via URScript commands.

    This class provides methods to send movement and other commands to a UR robot
    by establishing a socket connection to the robot's primary interface (port 30002).

    It is designed to be used as a context manager to ensure that the
    socket connection is properly closed.

    Example:
        >>> robot_ip = "192.168.1.102"  # Replace with your robot's IP
        >>> home_joints = [0, -1.5707, 0, -1.5707, 0, 0]
        >>> target_pose = [0.4, 0.2, 0.3, 0, 3.14, 0] # p[x, y, z, rx, ry, rz]
        >>>
        >>> with UniversalRobot(robot_ip) as robot:
        >>>     print("Moving to home position...")
        >>>     robot.movej(home_joints)
        >>>     print("Moving to target pose...")
        >>>     robot.movel(target_pose)
    """

    def __init__(self, host: str, port: int = 30002):
        """
        Initializes the UniversalRobot controller.

        Args:
            host (str): The IP address of the UR robot.
            port (int): The port for the primary interface (default is 30002).
        """
        self.host = host
        self.port = port
        self._socket = None
        self.command_timeout = 0.5 # Seconds to wait between commands
        self.plane = None # The active base coordinate system for relative moves

    def __enter__(self):
        """
        Enters the context manager, establishing a connection to the robot.
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exits the context manager, closing the connection to the robot.
        """
        self.disconnect()

    def connect(self):
        """
        Establishes a socket connection to the robot.
        """
        if self._socket is not None:
            print("Already connected.")
            return

        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(5) # Set a timeout for the connection attempt
            self._socket.connect((self.host, self.port))
            print(f"Successfully connected to UR robot at {self.host}:{self.port}")
        except socket.error as e:
            print(f"Error connecting to robot: {e}")
            self._socket = None
            raise

    def disconnect(self):
        """
        Closes the socket connection to the robot.
        """
        if self._socket:
            self._socket.close()
            self._socket = None
            print("Disconnected from UR robot.")

    def send_command(self, command: str):
        """
        Sends a URScript command to the robot.

        Args:
            command (str): The URScript command string.
        """
        if not self._socket:
            raise ConnectionError("Not connected to the robot. Call connect() first.")
        
        if not command.endswith('\n'):
            command += '\n'
            
        try:
            self._socket.sendall(command.encode('utf-8'))
            time.sleep(self.command_timeout) # Give the robot time to process
        except socket.error as e:
            print(f"Error sending command: {e}")
            raise

    def movej(self, q: PoseOrJoints, a: float = 1.4, v: float = 1.05, t: float = 0, r: float = 0):
        """
        Move to joint position (linear in joint space).

        Args:
            q (list/tuple): Joint positions in radians.
            a (float): Joint acceleration of leading axis [rad/s^2].
            v (float): Joint speed of leading axis [rad/s].
            t (float): Time [s]. If t > 0, 'a' and 'v' are ignored.
            r (float): Blend radius [m].
        """
        command = f"movej({list(q)}, a={a}, v={v}, t={t}, r={r})"
        self.send_command(command)

    def movel(self, pose: PoseOrJoints, a: float = 1.2, v: float = 0.25, t: float = 0, r: float = 0):
        """
        Move to a pose (linear in tool-space).

        If a plane is set on the class instance (using set_plane()),
        the move is relative to that pose. Otherwise, it is an absolute move.

        Args:
            pose (list/tuple): Target pose p[x, y, z, rx, ry, rz].
            a (float): Tool acceleration [m/s^2].
            v (float): Tool speed [m/s].
            t (float): Time [s]. If t > 0, 'a' and 'v' are ignored.
            r (float): Blend radius [m].
        """
        if self.plane:
            command = f"movel(pose_trans(p{list(self.plane)}, p{list(pose)}), a={a}, v={v}, t={t}, r={r})"
        else:
            command = f"movel(p{list(pose)}, a={a}, v={v}, t={t}, r={r})"
        self.send_command(command)

    def movep(self, pose: PoseOrJoints, a: float = 1.2, v: float = 0.25, r: float = 0):
        """
        Move to position (linear in tool-space) with circular blend.

        If a plane is set on the class instance (using set_plane()),
        the move is relative to that pose. Otherwise, it is an absolute move.

        Args:
            pose (list/tuple): Target pose p[x, y, z, rx, ry, rz].
            a (float): Tool acceleration [m/s^2].
            v (float): Tool speed [m/s].
            r (float): Blend radius [m].
        """
        if self.plane:
            command = f"movep(pose_trans(p{list(self.plane)}, p{list(pose)}), a={a}, v={v}, r={r})"
        else:
            command = f"movep(p{list(pose)}, a={a}, v={v}, r={r})"
        self.send_command(command)

    def speedj(self, qd: PoseOrJoints, a: float = 0.5, t: float = 0.1):
        """
        Accelerate to and maintain a joint speed.

        Args:
            qd (list/tuple): Joint speeds [rad/s].
            a (float): Joint acceleration [rad/s^2] (of leading axis).
            t (float): Time [s] before the robot comes to a stop.
        """
        command = f"speedj({list(qd)}, a={a}, t={t})"
        self.send_command(command)

    def speedl(self, xd: PoseOrJoints, a: float = 0.5, t: float = 0.1):
        """
        Accelerate to and maintain a tool speed.

        Args:
            xd (list/tuple): Tool speed [m/s, rad/s].
            a (float): Tool acceleration [m/s^2].
            t (float): Time [s] before the robot comes to a stop.
        """
        command = f"speedl({list(xd)}, a={a}, t={t})"
        self.send_command(command)

    def stopj(self, a: float = 2.0):
        """
        Stop (linear in joint space).

        Args:
            a (float): Joint deceleration [rad/s^2].
        """
        command = f"stopj({a})"
        self.send_command(command)

    def stopl(self, a: float = 2.0):
        """
        Stop (linear in tool space).

        Args:
            a (float): Tool deceleration [m/s^2].
        """
        command = f"stopl({a})"
        self.send_command(command)

    def set_tcp(self, pose: PoseOrJoints):
        """
        Set the Tool Center Point (TCP).

        Args:
            pose (list/tuple): TCP pose p[x, y, z, rx, ry, rz] relative to the flange.
        """
        command = f"set_tcp(p{list(pose)})"
        self.send_command(command)

    def set_target_payload(self, mass: float, cog: PoseOrJoints, inertia: PoseOrJoints = [0, 0, 0, 0, 0, 0], transition_time: float = 0.0):
        """
        Set the payload mass and center of gravity (CoG).
        This uses the set_target_payload() URScript function.
        
        Args:
            mass (float): Mass of the payload in kilograms.
            cog (list/tuple): Center of Gravity [x, y, z] in meters relative to
                              the tool flange.
            inertia (list/tuple, optional): The inertia tensor of the payload
                                            [Ixx, Iyy, Izz, Ixy, Ixz, Iyz].
            transition_time (float, optional): Time in seconds to transition to
                                               the new payload settings.
        """
        command = f"set_target_payload({mass}, {list(cog)}, {list(inertia)}, {transition_time})"
        self.send_command(command)

    def set_gravity(self, gravity: PoseOrJoints):
        """
        Set the direction of gravity for the robot's dynamics model.

        Args:
            gravity (list/tuple): Gravity vector [gx, gy, gz] in m/s^2.
                                  For a level robot, this is typically [0, 0, 9.82].
        """
        if len(gravity) != 3:
            raise ValueError("Gravity vector must have 3 elements [gx, gy, gz]")
        command = f"set_gravity({list(gravity)})"
        self.send_command(command)

    def set_command_timeout(self, timeout: float):
        """
        Sets the time to wait between sending commands.

        A small delay between commands can be necessary to allow the robot
        controller to process them.

        Args:
            timeout (float): The time in seconds to wait. Must be non-negative.
        """
        self.command_timeout = max(0.1, timeout)
        print(f"Command timeout set to: {self.command_timeout}s")

    def set_plane(self, pose: PoseOrJoints):
        """
        Sets a base coordinate system for subsequent relative moves.

        All future movel and movep commands will be executed relative to this pose
        until clear_plane() is called.

        Args:
            pose (list/tuple): The base coordinate system p[x, y, z, rx, ry, rz].
        """
        self.plane = pose
        print(f"Base pose set to: {self.plane}")

    def clear_plane(self):
        """
        Clears the base coordinate system.

        All future movel and movep commands will be executed in the robot's
        base coordinate system (absolute moves).
        """
        if self.plane:
            print(f"Clearing base pose: {self.plane}")
            self.plane = None
        else:
            print("No base pose was set.")

    def set_digital_out(self, pin: int, value: bool):
        """
        Sets a standard digital output on the robot controller.

        Args:
            pin (int): The digital output pin number (0-7).
            value (bool): The value to set the pin to (True for ON, False for OFF).
        """
        command = f"set_digital_out({pin}, {value})"
        self.send_command(command)

    def gripper_open(self, pin: int = 0, wait: float = 1.0):
        """
        Opens a gripper by setting a digital output to False.

        Args:
            pin (int): The digital output pin connected to the gripper.
            wait (float): Time in seconds to wait for the gripper to open.
        """
        print(f"Opening gripper on pin {pin}...")
        self.set_digital_out(pin, False)
        time.sleep(wait)

    def gripper_close(self, pin: int = 0, wait: float = 1.0):
        """
        Closes a gripper by setting a digital output to True.

        Args:
            pin (int): The digital output pin connected to the gripper.
            wait (float): Time in seconds to wait for the gripper to close.
        """
        print(f"Closing gripper on pin {pin}...")
        self.set_digital_out(pin, True)
        time.sleep(wait)


if __name__ == '__main__':
    # --- Example Usage ---
    # IMPORTANT: Replace with your robot's actual IP address.
    # Ensure the robot is in a safe state and you have a physical emergency stop available.
    ROBOT_IP = "192.168.1.102" # <-- CHANGE THIS

    # Define some positions
    # Note: These are example values. Adjust them for your specific setup and safety constraints.
    home_joint_position = [0, -1.5707, 1.5707, -1.5707, -1.5707, 0] # A "home" or "zero" position
    pose1 = [0.3, -0.2, 0.2, 3.14, 0, 0] # p[x, y, z, rx, ry, rz]
    pose2 = [0.4, -0.2, 0.3, 3.14, 0, 0] # p[x, y, z, rx, ry, rz]
    pose3 = [0.4,  0.2, 0.3, 3.14, 0, 0] # p[x, y, z, rx, ry, rz]
    plane_pose = [0.4, 0.0, 0.2, 0, 3.14, 0] # A custom plane/feature
    GRIPPER_PIN = 0 # The digital output pin your gripper is connected to

    try:
        with UniversalRobot(ROBOT_IP) as robot:
            print("--- Starting Robot Movement Sequence ---")

            # 1. Move to a known starting joint position
            print("Moving to home position...")
            robot.movej(home_joint_position, v=1.0)
            
            # 2. Move above a pick-up location
            print("Moving to pick-up approach pose...")
            robot.movel(pose1, v=0.25)
            
            # 3. Open the gripper
            robot.gripper_open(pin=GRIPPER_PIN)

            # 4. Move down to pick up the object
            print("Moving down to grasp object...")
            robot.movel([0, 0, -0.05], plane=pose1, v=0.1) # Relative move 5cm down

            # 5. Close the gripper
            robot.gripper_close(pin=GRIPPER_PIN)

            # 6. Move back up
            print("Moving up with object...")
            robot.movel(pose1, v=0.1)

            # 6. Return to the home position
            print("Returning to home position...")
            robot.movej(home_joint_position, v=1.0)
            
            print("--- Robot Movement Sequence Complete ---")

    except ConnectionError as e:
        print(f"Could not connect to the robot: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
