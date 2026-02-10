# ur_robot.py
import rtde_control
import rtde_io
import rtde_receive
import time
from typing import List, Tuple, Union
import numpy as np
import math

# Define a type hint for pose or joint configurations
PoseOrJoints = Union[List[float], Tuple[float, ...]]

def pose_trans(plane, target):
    """
    Transforms a target pose (relative to plane) into the base frame.
    Mimics URScript pose_trans(plane, target).
    
    Args:
        plane: [x, y, z, rx, ry, rz] of the reference plane
        target: [x, y, z, rx, ry, rz] of the target relative to the plane
    Returns:
        [x, y, z, rx, ry, rz] in the base frame
    """
    def vec_to_mat(rot_vec):
        theta = np.linalg.norm(rot_vec)
        if theta < 1e-6:
            return np.eye(3)
        k = rot_vec / theta
        K = np.array([
            [0, -k[2], k[1]],
            [k[2], 0, -k[0]],
            [-k[1], k[0], 0]
        ])
        return np.eye(3) + np.sin(theta) * K + (1 - np.cos(theta)) * np.dot(K, K)

    def mat_to_vec(R):
        val = (np.trace(R) - 1) / 2
        val = np.clip(val, -1.0, 1.0)
        theta = math.acos(val)
        if theta < 1e-6:
            return np.zeros(3)
        
        # Check for gimbal lock
        if abs(theta - math.pi) < 1e-6:
            # When theta is close to pi, there are multiple solutions for the rotation axis.
            # A robust implementation might handle this case differently,
            # but for many applications, a simplified approach can work.
            # Here we are not implementing a specific gimbal lock solution,
            # and depending on the robot's orientation, this might lead to
            # unpredictable behavior. A more robust solution can be found in
            # libraries like scipy.spatial.transform.Rotation
            pass

        # Avoid division by zero if sin(theta) is very small
        if math.sin(theta) < 1e-6:
            return np.zeros(3)
            
        factor = theta / (2 * math.sin(theta))
        rx = (R[2, 1] - R[1, 2]) * factor
        ry = (R[0, 2] - R[2, 0]) * factor
        rz = (R[1, 0] - R[0, 1]) * factor
        return np.array([rx, ry, rz])

    # Extract positions and rotations
    p_plane, r_plane = np.array(plane[:3]), np.array(plane[3:])
    p_target, r_target = np.array(target[:3]), np.array(target[3:])

    # Create homogeneous transformation matrices
    T_plane = np.eye(4)
    T_plane[:3, :3] = vec_to_mat(r_plane)
    T_plane[:3, 3] = p_plane

    T_target = np.eye(4)
    T_target[:3, :3] = vec_to_mat(r_target)
    T_target[:3, 3] = p_target

    # Multiply: Base -> Plane -> Target
    T_result = np.dot(T_plane, T_target)

    # Extract result
    pos_res = T_result[:3, 3].tolist()
    rot_res = mat_to_vec(T_result[:3, :3]).tolist()

    return pos_res + rot_res


class UniversalRobot:
    """
    A class to control a Universal Robot (UR) using the ur_rtde library.

    This class provides methods to send movement and other commands to a UR robot
    by establishing a connection to the robot's RTDE interface.

    It is designed to be used as a context manager to ensure that the
    connection is properly closed.

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

    def __init__(self, host: str,port: int = 30002):
        """
        Initializes the UniversalRobot controller.

        Args:
            host (str): The IP address of the UR robot.
        """
        self.host = host
        self.rtde_c = None
        self.rtde_io = None
        self.rtde_r = None
        self.command_timeout = 0 # Not used with rtde
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
        Establishes a connection to the robot.
        """
        if self.rtde_c and self.rtde_c.isConnected():
            print("Already connected.")
            return

        try:
            self.rtde_c = rtde_control.RTDEControlInterface(self.host)
            self.rtde_io = rtde_io.RTDEIOInterface(self.host)
            self.rtde_r = rtde_receive.RTDEReceiveInterface(self.host)
            print(f"Successfully connected to UR robot at {self.host}")
        except Exception as e:
            print(f"Error connecting to robot: {e}")
            self.rtde_c = None
            self.rtde_io = None
            self.rtde_r = None
            raise

    def disconnect(self):
        """
        Closes the connection to the robot.
        """
        if self.rtde_c and self.rtde_c.isConnected():
            self.rtde_c.disconnect()
            self.rtde_r.disconnect()
            # rtde_io does not have a disconnect method
            print("Disconnected from UR robot.")

    def movej(self, q: PoseOrJoints, a: float = 1.4, v: float = 1.05, t: float = 0, r: float = 0):
        """
        Move to joint position (linear in joint space).

        Args:
            q (list/tuple): Joint positions in radians.
            a (float): Joint acceleration of leading axis [rad/s^2].
            v (float): Joint speed of leading axis [rad/s].
            t (float): Time [s]. If t > 0, 'a' and 'v' are ignored. Not directly supported by rtde moveJ, but async moveJ with wait can be used.
            r (float): Blend radius [m].
        """
        self.rtde_c.moveJ(q, v, a, r)


    def movel(self, pose: Union[PoseOrJoints, List[PoseOrJoints]], a: float = 1.2, v: float = 0.25, t: float = 0, r: float = 0):
        """
        Move to a pose (linear in tool-space).

        If a plane is set on the class instance (using set_plane()),
        the move is relative to that pose. Otherwise, it is an absolute move.

        Args:
            pose (list/tuple or list of list/tuple): Target pose(s) p[x, y, z, rx, ry, rz].
                Can be a single pose or a list of poses to move through sequentially.
            a (float): Tool acceleration [m/s^2].
            v (float): Tool speed [m/s].
            t (float): Time [s]. If t > 0, 'a' and 'v' are ignored. Not supported by rtde moveL.
            r (float): Blend radius [m].
        """
        # Check if pose is a list of poses (list of lists/tuples) or a single pose
        is_list_of_poses = (isinstance(pose, list) and len(pose) > 0 and 
                           isinstance(pose[0], (list, tuple)))
        
        if is_list_of_poses:
            # Handle list of poses - transform all then send as list
            # Note: moveL(path) only accepts the path and asynchronous flag
            transformed_poses = []
            for target_pose in pose:
                if self.plane:
                    target_pose = pose_trans(self.plane, target_pose)
                transformed_poses.append(target_pose + [v, a, r])
            self.rtde_c.moveL(transformed_poses)
        else:
            # Handle single pose
            target_pose = pose
            if self.plane:
                target_pose = pose_trans(self.plane, pose)
            self.rtde_c.moveL(target_pose, v, a)

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
        target_pose = pose
        if self.plane:
            target_pose = pose_trans(self.plane, pose)
            
        self.rtde_c.moveP(target_pose, v, a, r)


    def movec(self, via_pose: PoseOrJoints, to_pose: PoseOrJoints, a: float = 1.2, v: float = 0.25, r: float = 0):
        """
        Circular move through an intermediate via pose to a target pose (movec).

        If `set_plane()` has been used, the poses will be transformed
        relative to that base pose similar to `movel`/`movep`.

        Args:
            via_pose (list/tuple): Intermediate pose on the circular arc p[x,y,z,rx,ry,rz].
            to_pose (list/tuple): Target pose p[x,y,z,rx,ry,rz].
            a (float): Tool acceleration [m/s^2].
            v (float): Tool speed [m/s].
            r (float): Blend radius [m].
        """
        final_via_pose = via_pose
        final_to_pose = to_pose

        if self.plane:
            final_via_pose = pose_trans(self.plane, via_pose)
            final_to_pose = pose_trans(self.plane, to_pose)

        self.rtde_c.moveC(final_via_pose, final_to_pose, v, a, r)


    def speedj(self, qd: PoseOrJoints, a: float = 0.5, t: float = 0.1):
        """
        Accelerate to and maintain a joint speed.

        Args:
            qd (list/tuple): Joint speeds [rad/s].
            a (float): Joint acceleration [rad/s^2] (of leading axis).
            t (float): Time [s] before the robot comes to a stop.
        """
        self.rtde_c.speedJ(qd, a, t)

    def speedl(self, xd: PoseOrJoints, a: float = 0.5, t: float = 0.1):
        """
        Accelerate to and maintain a tool speed.

        Args:
            xd (list/tuple): Tool speed [m/s, rad/s].
            a (float): Tool acceleration [m/s^2].
            t (float): Time [s] before the robot comes to a stop.
        """
        self.rtde_c.speedL(xd, a, t)

    def stopj(self, a: float = 2.0):
        """
        Stop (linear in joint space).

        Args:
            a (float): Joint deceleration [rad/s^2].
        """
        self.rtde_c.stopJ(a)

    def stopl(self, a: float = 2.0):
        """
        Stop (linear in tool space).

        Args:
            a (float): Tool deceleration [m/s^2].
        """
        self.rtde_c.stopL(a)

    def stop(self):
        """
        Stops the script on the robot controller.
        """
        self.rtde_c.stopScript()

    def send_script(self, script: str):
        """
        Sends a URScript to the robot.

        Args:
            script (str): The URScript to send.
        """
        self.rtde_c.sendScript(script)

    def set_tcp(self, pose: PoseOrJoints):
        """
        Set the Tool Center Point (TCP).

        Args:
            pose (list/tuple): TCP pose p[x, y, z, rx, ry, rz] relative to the flange.
        """
        self.rtde_c.setTcp(pose)

    def set_target_payload(self, mass: float, cog: PoseOrJoints, inertia: PoseOrJoints = [0, 0, 0, 0, 0, 0]):
        """
        Set the payload mass and center of gravity (CoG).
        
        Args:
            mass (float): Mass of the payload in kilograms.
            cog (list/tuple): Center of Gravity [x, y, z] in meters relative to
                              the tool flange.
            inertia (list/tuple, optional): This is not supported by the rtde library, but kept for compatibility.
        """
        self.rtde_c.setPayload(mass, cog)


    def set_gravity(self, gravity: PoseOrJoints):
        """
        Set the direction of gravity for the robot's dynamics model.

        Args:
            gravity (list/tuple): Gravity vector [gx, gy, gz] in m/s^2.
                                  For a level robot, this is typically [0, 0, 9.82].
        """
        if len(gravity) != 3:
            raise ValueError("Gravity vector must have 3 elements [gx, gy, gz]")
        self.rtde_c.setGravity(gravity)

    def set_command_timeout(self, timeout: float):
        """
        Sets the time to wait between sending commands.
        This is not used with the rtde library, but is kept for compatibility.
        """
        print("Command timeout is not used with the rtde library.")


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
        self.rtde_io.setStandardDigitalOut(pin, value)

    def get_digital_in(self, pin: int) -> bool:
        """
        Gets the state of a standard digital input.

        Args:
            pin (int): The digital input pin number (0-7).

        Returns:
            bool: The state of the digital input (True for HIGH, False for LOW).
        """
        # Ensure the required input is in the recipe
        if "actual_digital_input_bits" not in self.rtde_r.get_recipe_items():
            raise Exception("The 'actual_digital_input_bits' item is not in the RTDE recipe. Please add it to the recipe to use this function.")
        
        digital_in_bits = self.rtde_r.getActualDigitalInputBits()
        if digital_in_bits is None:
            raise ConnectionAbortedError("Failed to get digital input bits. Check connection and recipe.")
            
        return (digital_in_bits >> pin) & 1 == 1

    def getDigitalInState(self, pin: int) -> bool:
        """
        Alias for get_digital_in for compatibility.
        """
        return self.get_digital_in(pin)

    def get_analog_in(self, pin: int, min_val: float = 0.0, max_val: float = 10.0) -> float:
        """
        Gets the value of a standard analog input, optionally scaled to a range.

        Args:
            pin (int): The analog input pin number (e.g., 0 or 1).
            min_val (float): The minimum value of the scaled range.
            max_val (float): The maximum value of the scaled range.

        Returns:
            float: The scaled value of the analog input.
        """
        recipe = self.rtde_r.get_recipe_items()
        analog_input_name = f'standard_analog_input_{pin}'

        if analog_input_name not in recipe:
            raise Exception(f"The '{analog_input_name}' item is not in the RTDE recipe. Please add it to the recipe.")

        # The RTDE receive interface provides specific getters based on the recipe
        getter_name = f'get{analog_input_name.replace("_", " ").title().replace(" ", "")}'
        
        try:
            getter = getattr(self.rtde_r, getter_name)
        except AttributeError:
            raise Exception(f"Could not find a getter method '{getter_name}' on the RTDEReceiveInterface.")
        
        raw_value = getter()
        if raw_value is None:
            raise ConnectionAbortedError(f"Failed to get analog input {pin}. Check connection and recipe.")
        
        # Raw value is typically a voltage (e.g., 0-10V) or current (e.g., 4-20mA).
        # Here we assume a simple linear scaling.
        # For a 0-10V input, raw_value is the voltage.
        # For a 4-20mA input, this would need to be adjusted.
        return min_val + (max_val - min_val) * (raw_value / 10.0)

    def getAnalogInState(self, pin: int, min_val: float = 0.0, max_val: float = 10.0) -> float:
        """
        Alias for get_analog_in for compatibility.
        """
        return self.get_analog_in(pin, min_val, max_val)

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

