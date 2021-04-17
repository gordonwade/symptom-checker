// Utilities to help with data processing

export function getRiskTier(item, selectedSymptoms) {
    let avgScore = item.weighted_score/selectedSymptoms.length;

    switch (true) {
        case (avgScore < 2):
            return "Very Low";
        case (avgScore < 6):
            return "Low";
        case (avgScore < 9):
            return "Moderate";
        default:
            return "High";
    }
}
