"""
Quick connection test to Raspberry Pi
Checks if the Pi camera server is running and accessible.

Usage:
    python test_pi_connection.py --ip 192.168.137.230
"""

import socket
import sys

def test_port(ip, port, service_name):
    """Test if a port is open on the Pi."""
    print(f"\nTesting {service_name} (port {port})...")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    
    try:
        result = sock.connect_ex((ip, port))
        
        if result == 0:
            print(f"  ✓ Port {port} is OPEN - {service_name} is running!")
            sock.close()
            return True
        else:
            print(f"  ✗ Port {port} is CLOSED")
            print(f"     The {service_name} doesn't appear to be running")
            sock.close()
            return False
            
    except socket.timeout:
        print(f"  ✗ Connection timed out")
        print(f"     Check if Pi is on the same network")
        return False
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def main():
    if len(sys.argv) < 2:
        print("Usage: python test_pi_connection.py <pi_ip_address>")
        print("\nExample:")
        print("  python test_pi_connection.py 192.168.137.230")
        sys.exit(1)
    
    pi_ip = sys.argv[1]
    
    print("=" * 60)
    print(f" Testing Raspberry Pi Connection: {pi_ip}")
    print("=" * 60)
    
    # Test video port
    video_open = test_port(pi_ip, 8889, "Video Stream")
    
    # Test command port  
    command_open = test_port(pi_ip, 8890, "Command Server")
    
    print("\n" + "=" * 60)
    print(" Results Summary:")
    print("=" * 60)
    
    if video_open and command_open:
        print("\n✅ SUCCESS! Both ports are open.")
        print("\nThe Pi camera server is running and ready!")
        print("\nNow run:")
        print(f"  python pi_camera_client.py --ip {pi_ip}")
    else:
        print("\n❌ FAILED! One or more ports are not open.")
        print("\nTo fix this, on your Raspberry Pi run:")
        print("  cd ~/BlindStick")
        print("  python3 pi_camera_server.py")
        print("\nThen try this test again.")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()
