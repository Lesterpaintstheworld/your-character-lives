"""Audio device management"""
import queue
import pyaudio
import logging
from typing import List, Dict, Optional

class DeviceManager:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.input_devices = []
        self.output_devices = []
        self.refresh_devices()
        
    def refresh_devices(self):
        """Scan for working input and output devices"""
        self.input_devices = self._scan_input_devices()
        self.output_devices = self._scan_output_devices()
        
    def _scan_input_devices(self):
        """Scan for working input devices"""
        devices = []
        logging.info("Scanning for working audio input devices...")
        
        # Test default device first
        try:
            default_info = self.p.get_default_input_device_info()
            if self._test_input_device(default_info['index']):
                devices.append({
                    'index': default_info['index'],
                    'name': f"{default_info['name']} (Default)",
                    'channels': default_info['maxInputChannels'],
                    'rate': int(default_info['defaultSampleRate'])
                })
        except Exception as e:
            logging.warning(f"Default input device test failed: {e}")
            
        # Scan other devices
        for i in range(self.p.get_device_count()):
            try:
                device_info = self.p.get_device_info_by_index(i)
                if device_info['maxInputChannels'] == 0:
                    continue
                    
                if self._test_input_device(i):
                    devices.append({
                        'index': i,
                        'name': device_info['name'],
                        'channels': device_info['maxInputChannels'],
                        'rate': int(device_info['defaultSampleRate'])
                    })
                    logging.info(f"Found working device: {device_info['name']}")
            except Exception as e:
                logging.debug(f"Skipping device {i}: {e}")
                
        return devices
        
    def _scan_output_devices(self):
        """Scan for working output devices"""
        devices = []
        logging.info("Scanning for working audio output devices...")
        
        # Test default device first
        try:
            default_info = self.p.get_default_output_device_info()
            if self._test_output_device(default_info['index']):
                devices.append({
                    'index': default_info['index'],
                    'name': f"{default_info['name']} (Default)",
                    'channels': default_info['maxOutputChannels'],
                    'rate': int(default_info['defaultSampleRate'])
                })
        except Exception as e:
            logging.warning(f"Default output device test failed: {e}")
            
        # Scan other devices
        for i in range(self.p.get_device_count()):
            try:
                device_info = self.p.get_device_info_by_index(i)
                if device_info['maxOutputChannels'] == 0:
                    continue
                    
                if self._test_output_device(i):
                    devices.append({
                        'index': i,
                        'name': device_info['name'],
                        'channels': device_info['maxOutputChannels'],
                        'rate': int(device_info['defaultSampleRate'])
                    })
                    logging.info(f"Found working device: {device_info['name']}")
            except Exception as e:
                logging.debug(f"Skipping device {i}: {e}")
                
        return devices
        
    def _test_input_device(self, device_index):
        """Test if an input device works"""
        try:
            test_stream = self.p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=1024,
                start=False
            )
            test_stream.close()
            return True
        except Exception as e:
            logging.debug(f"Input device {device_index} test failed: {e}")
            return False
            
    def _test_output_device(self, device_index):
        """Test if an output device works"""
        try:
            test_stream = self.p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                output=True,
                output_device_index=device_index,
                frames_per_buffer=1024,
                start=False
            )
            test_stream.close()
            return True
        except Exception as e:
            logging.debug(f"Output device {device_index} test failed: {e}")
            return False
            
    def get_default_input_device(self):
        """Get the default input device if working"""
        try:
            default_info = self.p.get_default_input_device_info()
            if self._test_input_device(default_info['index']):
                return default_info['index']
        except:
            pass
        return None
        
    def get_default_output_device(self):
        """Get the default output device if working"""
        try:
            default_info = self.p.get_default_output_device_info()
            if self._test_output_device(default_info['index']):
                return default_info['index']
        except:
            pass
        return None
        
    def cleanup(self):
        """Clean up resources"""
        if self.p:
            self.p.terminate()
