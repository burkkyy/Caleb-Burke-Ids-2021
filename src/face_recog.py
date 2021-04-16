import face_recognition
import cv2

'''
In FaceRecog, a face, or identity object takes the form:
    (location of face, face_encoding, name of face)
    
face_recognition works by using the dlib library and your gpu to run a convolutional neural network on yo face. In the 
future I plan on creating my own cnn from scratch but I would need more time for that as I STILL DON'T KNOW HOW TO RUN 
STUFF ON THE GPU.
'''


def create_encoding(image):
    # ONLY INPUT IMAGES THAT FOR SURE HAVE ONE HIGHLY VISIBLE FACE
    location = face_recognition.face_locations(image, model="cnn")
    encoding = face_recognition.face_encodings(image, location)[0]
    return encoding


def create_encoding_list(image):
    locations = face_recognition.face_locations(image, model="cnn")
    encodings = face_recognition.face_encodings(image, locations)
    return encodings


def draw_rect_on_people(image):
    """
    :param image: the image to scan
    :return: the new image with rects on faces
    """

    face_locations = face_recognition.face_locations(image, model="cnn")

    # loop over the face locations found
    for face_location, index in zip(face_locations, range(len(face_locations))):
        color = (100, 255, 0)  # the color of the rect
        if index == 0:  # the first face found shall have a red box
            color = (0, 0, 255)

        # draw rect around face
        top_left = (face_location[3], face_location[0])
        bottom_right = (face_location[1], face_location[2])
        cv2.rectangle(image, top_left, bottom_right, color, 1)

        # draw a little box below rect
        top_left = (face_location[3], face_location[2])
        bottom_right = (face_location[1], face_location[2] + 22)
        cv2.rectangle(image, top_left, bottom_right, color, cv2.FILLED)

        # display the face number in the little box
        cv2.putText(
            image, f"FACE NUMBER: {index}", (face_location[3] + 10, face_location[2] + 15),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (41, 41, 41), 1, cv2.LINE_AA
        )

    return image


def draw_rect_on_people_with_names(image, known_face_names: list, known_face_encodings: list):
    """
    :param image: the image to scan
    :param known_face_names: corresponding names to know_face_encodings
    :param known_face_encodings: list of the face encodings
    :return: the image with stuff drawn on peoples faces
    """

    face_locations = face_recognition.face_locations(image, model="cnn")
    unknown_encodings = face_recognition.face_encodings(image, face_locations)

    for face_encoding, face_location in zip(unknown_encodings, face_locations):
        results = face_recognition.compare_faces(known_face_encodings, face_encoding, 0.6)  # returns a list of bools

        # draw box around face
        top_left = (face_location[3], face_location[0])
        bottom_right = (face_location[1], face_location[2])
        cv2.rectangle(image, top_left, bottom_right, (100, 255, 0), 1)

        # draw little box below face
        top_left = (face_location[3], face_location[2])
        bottom_right = (face_location[1], face_location[2] + 22)
        cv2.rectangle(image, top_left, bottom_right, (100, 255, 0), cv2.FILLED)

        # determine the name of the face in the image
        if True in results:
            cv2.putText(
                image, known_face_names[results.index(True)], (face_location[3] + 10, face_location[2] + 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (41, 41, 41), 1, cv2.LINE_AA
            )
        else:
            cv2.putText(
                image, "Unknown Face", (face_location[3] + 10, face_location[2] + 15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (41, 41, 41), 1, cv2.LINE_AA
            )

    return image


if __name__ == "__main__":
    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    # img = cv2.imread('./SOME IMAGE.jpg')
    # my_encoding = create_encoding(img)

    while True:
        ret, capture = cam.read()
        # capture = image_find_people(capture, [my_encoding, my_encoding1, my_encoding2], ["Caleb", "Jessica", "Aaron"])
        cv2.imshow("Face Test", capture)
        if cv2.waitKey(20) & 0xFF == 27:
            break

    cv2.destroyAllWindows()
    cam.release()
