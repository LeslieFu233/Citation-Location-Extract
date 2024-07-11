import Levenshtein

class SimilarityMeasure:
    """
    A class that calculates the similarity between two strings using the Levenshtein distance.

    Attributes:
        None

    Methods:
        calculate_similarity(string1, string2): Calculates the similarity between two strings.

    """

    def calculate_similarity(self, string1, string2):
        """
        Calculates the similarity between two strings using the Levenshtein distance.

        Args:
            string1 (str): The first string.
            string2 (str): The second string.

        Returns:
            float: The similarity score between the two strings.

        """
        distance =  Levenshtein.distance(string1, string2)/max(len(string1), len(string2))
        return 1 - distance
    
class BinaryMeasure:
    """
    A class that calculates the similarity between two strings using a binary measure.

    The similarity is calculated by comparing the two strings and returning 1 if they are equal, and 0 otherwise.
    """

    def calculate_similarity(self, string1, string2):
        """
        Calculates the similarity between two strings.

        Parameters:
        - string1 (str): The first string to compare.
        - string2 (str): The second string to compare.

        Returns:
        - int: The similarity between the two strings. Returns 1 if the strings are equal, and 0 otherwise.
        """
        if string1 == string2:
            return 1
        else:
            return 0


    