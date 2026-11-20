import socket
import sys

# Update these with your W2K-1 hostname/IP and configured TCP port
HOST = 'w2k-279953.local'
PORT = 60002


def parse_nmea_sentence(sentence):
  """Parses incoming NMEA 0183 sentences, focusing on GPS fixes ($GPRMC/GNRMC)."""
  sentence = sentence.strip()
  print(sentence)
  return
  if not sentence.startswith('$'):
    return

  # Split sentence by commas
  parts = sentence.split(',')
  talker_sent = parts[0]

  # Recommended Minimum Specific GNSS Data (RMC)
  if 'RMC' in talker_sent:
    try:
      utc_time = parts[1]
      status = parts[2]  # 'A' = Data Valid/Active, 'V' = Void
      lat = parts[3]
      lat_dir = parts[4]
      lon = parts[5]
      lon_dir = parts[6]
      sog = parts[7]  # Speed Over Ground (knots)
      cog = parts[8]  # Course Over Ground (degrees true)
      date = parts[9]

      if status == 'A':
        print(
            f'[GPS FIX] Date: {date} Time: {utc_time} UTC | Position:'
            f' {lat} {lat_dir}, {lon} {lon_dir} | SOG: {sog} kts | COG: {cog}°'
        )
      else:
        print(f'[GPS SEARCHING] Status: Void (No Fix Yet)')
    except IndexError:
      print(f'[PARSE ERROR] Malformed RMC sentence: {sentence}')


def main():
  print(f'Attempting connection to Actisense W2K-1 at {HOST}:{PORT}...')
  try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
      s.connect((HOST, PORT))
      print('Connected successfully! Listening for NMEA sentences...\n')

      buffer = ''
      while True:
        data = s.recv(1024)
        if not data:
          print('Connection closed by remote host.')
          break
        buffer += data.decode('ascii', errors='ignore')

        # Process complete lines from the TCP stream buffer
        while '\n' in buffer:
          line, buffer = buffer.split('\n', 1)
          parse_nmea_sentence(line)

  except KeyboardInterrupt:
    print('\nStream listener stopped by user.')
  except socket.gaierror:
    print(
        f'[ERROR] Could not resolve host "{HOST}". Verify the hostname or use'
        ' the gateway\'s IP address.'
    )
  except ConnectionRefusedError:
    print(
        f'[ERROR] Connection refused on {HOST}:{PORT}. Verify that the TCP'
        ' data server is enabled and the port matches.'
    )
  except Exception as e:
    print(f'[ERROR] Unexpected error: {e}')


if __name__ == '__main__':
  main()
