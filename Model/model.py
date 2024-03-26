from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense

def CreateModel(input_image_shape,num_classes ):
    model = Sequential()
    model.add( Conv2D(32, (3, 3), activation='relu', input_shape=input_image_shape))
    model.add(MaxPooling2D((2, 2)))
    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(MaxPooling2D((2, 2)))
    model.add(Conv2D(128, (3, 3), activation='relu'))
    model.add(MaxPooling2D((2, 2)))
    model.add(Flatten())
    model.add(Dense(128, activation='relu'))
    model.add(Dense(num_classes, activation='softmax'))
    return model