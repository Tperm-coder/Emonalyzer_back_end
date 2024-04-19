from app.config.settings import settings
import numpy as np
import pandas as pd
import numpy as np
import soundfile as sf
from scipy.io import wavfile
import keras
from keras.models import Sequential
from keras import layers
from keras import optimizers
from keras import callbacks 
from keras import regularizers
import matplotlib.pyplot as plt 
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix
import librosa
import librosa.display
import IPython.display as ipd
from IPython.display import Audio
import seaborn as sns
import os
import random
import csv
import re
import tempfile
import zipfile
from pydub import AudioSegment 
import tensorflow as tf

class PretrainedModel:
    def __init__(self, model_file = settings.MODEL_PATH):
        self.model = tf.keras.models.load_model(model_file)

    def feature_extraction_merged(self,file_path):
        # Initialize lists to store features and emotion labels
        zcr_list = []
        c_stft_list = []
        mfcc_list = []
        rms_list = []
        mel_list = []

        # Initialize variable to store the maximum length of features
        max_length = 0


        # Load audio data
        data, sample_rate = librosa.load(file_path)

        # Extract features
        zcr = librosa.feature.zero_crossing_rate(data)
        stft = np.abs(librosa.stft(data))
        c_stft = librosa.feature.chroma_stft(S=stft, sr=sample_rate)
        mfcc = librosa.feature.mfcc(y=data, sr=sample_rate, n_mfcc=13)  # Extract 13 MFCCs
        rms = librosa.feature.rms(y=data)
        mel = librosa.feature.melspectrogram(y=data, sr=sample_rate)

        # Update maximum length of features
        max_length = max(max_length, zcr.shape[1], c_stft.shape[1], mfcc.shape[1], rms.shape[1], mel.shape[1])

        # Append features and emotion labels to lists
        zcr_list.append(zcr)
        c_stft_list.append(c_stft)
        mfcc_list.append(mfcc)
        rms_list.append(rms)
        mel_list.append(mel)
    

        # Apply padding with zeros to features
        for feature_list in [zcr_list, c_stft_list, mfcc_list, rms_list, mel_list]:
            for i in range(len(feature_list)):
                feature = feature_list[i]
                if feature.shape[1] < max_length:
                    # Pad features with zeros
                    padding_width = max_length - feature.shape[1]
                    feature_list[i] = np.pad(feature, ((0, 0), (0, padding_width)), mode='constant')

        # Convert lists to numpy arrays
        zcr_array = np.array(zcr_list)
        c_stft_array = np.array(c_stft_list)
        mfcc_array = np.array(mfcc_list)
        rms_array = np.array(rms_list)
        mel_array = np.array(mel_list)

        return zcr_array, c_stft_array, mfcc_array, rms_array, mel_array

    def preprocessing_merged(self, zcr_array, c_stft_array, mfcc_array, rms_array, mel_array):
        #Scaling data to prepare it for the LSTM Model
        scaler = StandardScaler()

        # Reshape the arrays to 2D for scaling
        zcr_array_2d = zcr_array.reshape(zcr_array.shape[0], -1)
        c_stft_array_2d = c_stft_array.reshape(c_stft_array.shape[0], -1)
        mfcc_array_2d = mfcc_array.reshape(mfcc_array.shape[0], -1)
        rms_array_2d = rms_array.reshape(rms_array.shape[0], -1)
        mel_array_2d = mel_array.reshape(mel_array.shape[0], -1)

        # Scale the features
        zcr_scaled = scaler.fit_transform(zcr_array_2d)
        c_stft_scaled = scaler.fit_transform(c_stft_array_2d)
        mfcc_scaled = scaler.fit_transform(mfcc_array_2d)
        rms_scaled = scaler.fit_transform(rms_array_2d)
        mel_scaled = scaler.fit_transform(mel_array_2d)

        # Reshape the scaled arrays back to their original shapes
        zcr_array = zcr_scaled.reshape(zcr_array.shape)
        c_stft_array = c_stft_scaled.reshape(c_stft_array.shape)
        mfcc_array = mfcc_scaled.reshape(mfcc_array.shape)
        rms_array = rms_scaled.reshape(rms_array.shape)
        mel_array = mel_scaled.reshape(mel_array.shape)

        # Reshape arrays for LSTM input
        zcr_lstm = np.swapaxes(zcr_array, 1, 2)  # (579, 108, 1)
        c_stft_lstm = np.swapaxes(c_stft_array, 1, 2)  # (579, 108, 12)
        mfcc_lstm = np.swapaxes(mfcc_array, 1, 2)  # (579, 108, 13)
        rms_lstm = np.swapaxes(rms_array, 1, 2)  # (579, 108, 1)
        mel_lstm = np.swapaxes(mel_array, 1, 2)  # (579, 108, 128)
        
        return zcr_lstm, c_stft_lstm,  mfcc_lstm, rms_lstm, mel_lstm

    def concatenate_features(self, *features, axis =2 ):
        return np.concatenate(features, axis)

    def preprocess_input(self, file_path):
        zcr_array, c_stft_array, mfcc_array, rms_array, mel_array = self.feature_extraction_merged(file_path)
        zcr_lstm, c_stft_lstm,  mfcc_lstm, rms_lstm, mel_lstm = self.preprocessing_merged(zcr_array, c_stft_array, mfcc_array, rms_array, mel_array)
        X = self.concatenate_features(zcr_lstm, c_stft_lstm,  mfcc_lstm, rms_lstm, mel_lstm)
        return X

    def predict(self, file_path):
        print("Prediction emotion ===> " , file_path)
        preprocessed_data = self.preprocess_input(file_path)        
        predictions = self.model.predict(preprocessed_data)[0]
        print("=========================>" , predictions)
        emotions = {
            "ANG" : str(predictions[0]) , 
            "HAP" : str(predictions[1]) , 
            "NEU" : str(predictions[2]) , 
            "SAD" : str(predictions[3])
        }
        print(emotions)
        return emotions