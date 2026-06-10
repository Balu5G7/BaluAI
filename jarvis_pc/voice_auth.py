from resemblyzer import VoiceEncoder, preprocess_wav
import numpy as np

encoder = VoiceEncoder()

reference_wav = preprocess_wav("balu_voice.ogg")
reference_embedding = encoder.embed_utterance(reference_wav)

def is_balu(audio_file):
    test_wav = preprocess_wav(audio_file)
    test_embedding = encoder.embed_utterance(test_wav)

    similarity = np.dot(reference_embedding, test_embedding)

    print("Voice similarity:", similarity)

    return similarity > 0.75
