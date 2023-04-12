package part1;
import java.net.*;
import java.nio.*;

public class Project1 {

    // public static InetAddress serverAddress = InetAddress.getByName("attu2.cs.washington.edu");
    public static final int PORT = 12235;
    public static InetAddress SERVERADDRESS;
    public static final short STEP1 = 1;
	public static final short STEP2 = 2;
    public static final short DIGITS = 887;
    public static final int HEADERSIZE = 12;
    public static final int SERVERPACKAGESIZE = 16;
    public static void main(String[] args) throws Exception {
        // define the server address and port number
    }

    public static void p1StageA() throws Exception {
        //Step a1
        DatagramSocket socket = createUDPConnection();
        String message = "hello world";
        // send data to the server
        byte[] sendData = createHeader(message.getBytes(), 0, STEP1, DIGITS);
        DatagramPacket datagramPacket = new DatagramPacket(sendData, sendData.length, SERVERADDRESS, PORT);

        socket.send(datagramPacket);
        
        //Step a2
        // receive data from the server
        byte[] receiveData = new byte[HEADERSIZE + SERVERPACKAGESIZE];
        DatagramPacket receivePacket = new DatagramPacket(receiveData, receiveData.length);
        socket.receive(receivePacket);
        //Print out message
        ByteBuffer receivedBuffer =  ByteBuffer.wrap(receiveData); 
        receivedBuffer.position(HEADERSIZE);
        int num = receivedBuffer.getInt();
        int len = receivedBuffer.getInt();
        int udp_port = receivedBuffer.getInt();
        int secret = receivedBuffer.getInt();
        System.out.println("Stage A secret: " + secret);
        // close the socket
        socket.close();
    }

    public static DatagramSocket createUDPConnection() throws Exception {
        SERVERADDRESS = InetAddress.getByName("attu2.cs.washington.edu");
        DatagramSocket socket = new DatagramSocket();
        socket.connect(SERVERADDRESS, PORT);
        return socket;
        
    }
    // Need to fill 12 bytes of data before the message as the header
    // First 4 bytes is the len of the message
    public static byte[] createHeader(byte[] payload, int secret, short step, short digits) throws Exception {

        int payloadLen =  4 * ( payload.length / 4 + (int) Math.ceil((payload.length % 4)/ 4.0));
        // byte[] message = new byte[12 + payloadLen];
        ByteBuffer buffer = ByteBuffer.allocate(HEADERSIZE + payloadLen);
        buffer.putInt(payload.length);
        buffer.putInt(secret);
		buffer.putShort(step);
		buffer.putShort(digits);
		buffer.put(payload);
        return buffer.array();

    } 


}
