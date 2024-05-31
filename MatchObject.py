import Levenshtein
class SimilarityMeasure:
    def calculate_similarity(self, string1, string2):
        distance =  Levenshtein.distance(string1, string2)/max(len(string1), len(string2))
        return 1 - distance
class BinaryMeasure:
    def calculate_similarity(self, string1, string2):
        if string1 == string2: return 1
        else: return 0


    