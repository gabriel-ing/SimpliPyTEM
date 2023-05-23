import pandas as pd
from scipy.spatial import distance as dist

from SimpliPyTEM.Thresholding import *


class particle:
    def __init__(self, centroid, frame_number, frame_index):
        self.current_coordinate = centroid
        self.coordinates = [centroid]
        self.distances = [0]
        self.pixelsize = None
        self.frame_numbers = [frame_number]
        self.frame_indices = [frame_index]

    def update_coordinate(self, coordinate, frame_num, frame_index):
        self.distances.append(dist.euclidean(self.current_coordinate, coordinate))
        self.coordinates.append(coordinate)
        self.current_coordinate = coordinate
        self.frame_numbers.append(frame_num)
        self.frame_indices.append(frame_index)

    def length(self):
        return len(self.coordinates)

    def __len__(self):
        return len(self.coordinates)

    def mean_distance(self):
        mean = np.mean(self.distances)
        if self.pixelsize:
            mean = self.pixelsize * mean
        return mean

    def total_displacement(self):
        d = dist.euclidean(self.distances[0], self.current_coordinate)
        if self.pixelsize:
            d = d * self.pixelsize
        return d

    def get_area(self, data):
        areas = []
        for x in range(len(self.frame_numbers)):
            area = data["Area"][self.frame_numbers[x]][self.frame_indices[x]]
            areas.append(area)
        return area

    def get_height_widths(self, data):
        widths, heights = [], []
        for x in range(len(self.frame_numbers)):
            width = data["Width"][self.frame_numbers[x]][self.frame_indices[x]]
            height = data["Height"][self.frame_numbers[x]][self.frame_indices[x]]
            widths.append(width)
            heights.append(height)

        return widths, heights

    def get_feature(self, data, feature_key):
        property_list = []

        y_list = []
        for x in range(len(self.frame_numbers)):
            # print(x, len(self.frame_numbers), len(self.frame_indices))
            prop = data[feature_key][self.frame_numbers[x]][self.frame_indices[x]]
            if type(prop) == np.ndarray and len(prop) == 1:
                property_list.append(float(prop))
            elif type(prop) == np.ndarray and len(prop) == 2:
                property_list.append(prop[0])
                y_list.append(prop[1])
            else:
                property_list.append(prop)
        if y_list:
            return property_list, y_list
        else:
            return property_list

    def get_feature_data(self, data):
        df = pd.DataFrame()
        df["Frame number"] = self.frame_numbers
        for key in data.keys():
            props = self.get_feature(data, key)
            if type(props) != tuple:
                df[key] = props
            elif type(props) == tuple and key == "Centroid":
                df["Centroid_x"] = props[0]
                df["Centroid_y"] = props[1]
        if self.pixelsize:
            df["Displacement"] = self.distances * pixelsize
        else:
            df["Displacement (pix)"] = self.distances
        self.data_full = df
        return df


def get_particles(data, min_dist):
    # create the list of particles
    particle_list = []
    # It needs a list of current coordinates, I think this has to go here:
    coordinate_list = []

    # This is finding the centroids from the data, as this is the key value. This actually needs to be changed because I've changed it to centroid_x and centroid_y by default.

    centroids = data["Centroid"]

    # Compare the distances between the particles in two adjacent frames
    for x in range(len(centroids) - 1):
        dists = dist.cdist(centroids[x], centroids[x + 1])
        connectedx, connectedy = np.where(dists < min_dist)
        connected = list(zip(connectedx, connectedy))
        # print(connected)

        for i in connected:
            # print(i)
            coord1 = tuple(centroids[x][i[0]])
            coord2 = tuple(centroids[x + 1][i[1]])
            # print(coord1, coord2)

            if coord1 not in coordinate_list:
                p = particle(coord1, x, i[0])
                p.update_coordinate(coord2, x + 1, i[1])
                particle_list.append(p)
                coordinate_list.append(coord2)
            elif coord1 in coordinate_list:
                ind = coordinate_list.index(coord1)
                particle_list[ind].update_coordinate(coord2, x + 1, i[1])
                coordinate_list[ind] = coord2

    return particle_list


def extract_features(particle_list, data, features_list):
    extracted_features = {}
    for feature in features_list:
        extracted_features[feature] = []
    for p in particle_list:
        df = p.get_feature_data()
        for feature in features_list:
            extracted_features
