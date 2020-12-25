#!/usr/bin/env python
import rospy
import requests
import json
from std_msgs.msg import String
import os
from ngrok_ros.srv import StartTunnel, StartTunnelResponse


def start_tunnel_service(req):
    public_url = start_tunnel(req.addr, req.proto, req.name)
    response = StartTunnelResponse()
    response.public_url = public_url
    return response


def start_tunnel_callback(msg):
    addr, proto, name = msg.data.split(",")
    public_url = start_tunnel(addr, proto, name)
    response_msg = String()
    response_msg.data = public_url
    message_pub.publish(response_msg)


def start_tunnel(addr, proto, name):
    json_request = {"addr": addr, "proto": proto, "name": name}
    try:
        r = requests.post("http://localhost:4040/api/tunnels", json=json_request)
        public_url = r.json()["public_url"]
    except Exception as e:
        print(e)
        rospy.logerr("Check if ngrok is running and try again")
        public_url = ""
    return public_url


if __name__ == "__main__":
    rospy.init_node("ngrok_ros")
    message_pub = rospy.Publisher("/ngrok_ros/public_addr", String, queue_size=1, latch=True)
    rospy.Subscriber("/ngrok_ros/start_tunnel", String, start_tunnel_callback)
    port = rospy.get_param("~port", 9090)
    tunnel_name = rospy.get_param("~name", "ros_bridge")
    json_request = {"addr": str(port), "proto": "tcp", "name": tunnel_name}
    service_server = rospy.Service("ngrok_ros/start_tunnel", StartTunnel, start_tunnel_service)
    rospy.spin()

