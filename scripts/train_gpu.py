import tensorflow as tf
import matplotlib.pyplot as plt
import os
import sys

physical_devices = tf.config.list_physical_devices('GPU')
print("Num GPUs:", len(physical_devices))

args = sys.argv[1:]
dim = int(args[0]) #128
output_filename = args[1] #'fungi_pretrained_model'
batch_size = int(args[2]) #32

if dim == '':
    dim = 256
if output_filename == '':
    output_filename = 'fungi_trained_model'
if batch_size == '':
    batch_size = 8

if os.name == 'nt':
    prefix = 'D:/'
if os.name == 'posix':
    prefix = '/media/bob/WOLAND/'
if os.name == 'posix':
    data_dir = '/home/bob/fungi-id-ai/images_30_' + str(dim)
if os.name == 'nt':
    data_dir = prefix + '/PROJLIB/Python/fungi-id-ai/images_' + str(dim)

with tf.device("/gpu:0"):
    train_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=0.2,
        subset="training",
        seed=6666,
        image_size=(dim, dim),
        batch_size=batch_size)

    val_ds = tf.keras.utils.image_dataset_from_directory(
        data_dir,
        validation_split=0.2,
        subset="validation",
        seed=6666,
        image_size=(dim, dim),
        batch_size=batch_size)

    class_names = train_ds.class_names
    print(class_names)

    AUTOTUNE = tf.data.AUTOTUNE

    train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

    num_classes = len(class_names)


    in_shape = (dim, dim, 3)
    # base_model = tf.keras.applications.resnet50.ResNet50(include_top=False, weights='imagenet', input_shape=in_shape)

    data_augmentation = tf.keras.Sequential([
        tf.keras.layers.RandomFlip('horizontal'),
        tf.keras.layers.RandomRotation(0.44),
        tf.keras.layers.RandomZoom(0.25),
        tf.keras.layers.RandomContrast(factor=0.2), 
        tf.keras.layers.RandomBrightness(factor=0.2)
    ])

    callbacks = [tf.keras.callbacks.EarlyStopping(patience=10,
                                               monitor='val_accuracy',
                                               restore_best_weights=True)]

    model = tf.keras.Sequential([
        data_augmentation,
        tf.keras.layers.Rescaling(1./255, input_shape=(dim, dim, 3)),
        tf.keras.layers.Conv2D(64, 3, padding='same', activation='relu'),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Conv2D(96, 3, padding='same', activation='relu'),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Conv2D(128, 3, padding='same', activation='relu'),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Conv2D(192, 3, padding='same', activation='relu'),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Conv2D(256, 3, padding='same', activation='relu'),
        tf.keras.layers.MaxPooling2D(),
        tf.keras.layers.Dropout(0.13),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(dim, activation='relu'),
        tf.keras.layers.Dense(num_classes, name="outputs")
    ])

    # Compile the model
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])

    history = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=num_classes*10,
        #callbacks=callbacks
    )

    if os.name == 'posix':
        path = '/home/bob/fungi-id-ai/model/' + output_filename + '_' + str(dim) + '.h5'
    if os.name == 'nt':
        path = prefix + '/PROJLIB/Python/fungi-id-ai/model/' + output_filename + '_' + str(dim) + '.h5'

    model.save(path)
    model.summary()