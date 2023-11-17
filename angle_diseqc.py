import wave
import math
import subprocess


def angle_to_hex(angle):
    hex_string = "E" if angle <= 0 else "D"
    angle = abs(round(angle, 1))
    angle_int = int(angle)
    angle_frac = int((angle - angle_int) * 16)
    return hex_string + (hex(angle_int)[2:] + hex(angle_frac)[2:]).upper().zfill(3)


# generator that returns hex bit by bit plus parity bit
def bit_encoder(hex_input):
    # convert hexadecimal input to bytes
    byte_input = bytes.fromhex(hex_input)

    # iterate over bytes to read it byte by byte
    for byte in byte_input:
        # convert byte to binary string and strip the '0b' prefix
        binary_string = bin(byte)[2:]

        # pad the binary string with leading zeros to ensure it has 8 bits
        binary_string = binary_string.zfill(8)

        # count the number of 1 bits in the byte
        num_ones = binary_string.count("1")

        # calculate the parity bit as 0 or 1 depending on whether the count is even or odd
        parity_bit = "0" if num_ones % 2 == 0 else "1"

        # concatenate the parity bit to the end of the binary string
        binary_string += parity_bit

        # iterate over bits to read it bit by bit, including the parity bit
        for bit in binary_string:
            yield int(bit)


def move_rotor(angle):
    hex_input = "E0316E" + angle_to_hex(angle)
    # Set parameters for the wave file
    sample_rate = 198000
    num_channels = 1
    sample_width = 2

    # Set parameters for the sine wave and silence
    amplitude = 32767
    freq_hz = 20000
    num_sine_samples = int(sample_rate * 0.002)  # 5ms of sine wave

    # Generate the sine wave samples
    sine_samples = []
    for j in range(num_sine_samples):
        sample = int(amplitude * math.sin(2 * math.pi * freq_hz * j / sample_rate))
        sine_samples.append(sample)

    # Create a new wave file
    with wave.open("binary_wave.wav", "wb") as wave_file:
        wave_file.setnchannels(num_channels)
        wave_file.setsampwidth(sample_width)
        wave_file.setframerate(sample_rate)

        for bit in bit_encoder(hex_input):
            if bit:  # 0.5ms of sine signal + 1ms of silence
                for i in range(int(sample_rate * 0.0006)):
                    wave_file.writeframesraw(
                        sine_samples[i].to_bytes(2, byteorder="little", signed=True)
                    )
                for i in range(int(sample_rate * 0.001)):
                    wave_file.writeframesraw(b"\x00\x00")

            else:  # 1ms of sine signal + 0.5ms of silence
                for i in range(int(sample_rate * 0.0011)):
                    wave_file.writeframesraw(
                        sine_samples[i].to_bytes(2, byteorder="little", signed=True)
                    )
                for i in range(int(sample_rate * 0.0005)):
                    wave_file.writeframesraw(b"\x00\x00")

        for i in range(int(sample_rate * 0.006)):
            wave_file.writeframesraw(b"\x00\x00")

    wave_file.close()

    # Define the command to play the audio file using aplay
    command = ["play", "binary_wave.wav"]

    # Run the command as a subprocess
    subprocess.run(command)


if __name__ == "__main__":
    angle = float(input("Enter the angle: "))
    move_rotor(angle)
