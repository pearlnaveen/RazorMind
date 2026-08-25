def calculate_priority(
    recovery_probability,
    amount,
    anomaly=False
):

    score = 0

    # Recovery confidence
    if recovery_probability >= 0.90:
        score += 40

    elif recovery_probability >= 0.70:
        score += 30

    elif recovery_probability >= 0.50:
        score += 20

    else:
        score += 10

    # Financial impact
    if amount >= 50000:
        score += 40

    elif amount >= 20000:
        score += 30

    elif amount >= 10000:
        score += 20

    else:
        score += 10

    # Anomaly bonus
    if anomaly:
        score += 20

    # Final priority
    if score >= 70:
        priority = "CRITICAL"

    elif score >= 50:
        priority = "HIGH"

    elif score >= 30:
        priority = "MEDIUM"

    else:
        priority = "LOW"

    return {
        "score": score,
        "priority": priority
    }


if __name__ == "__main__":

    result = calculate_priority(
        recovery_probability=0.85,
        amount=30000,
        anomaly=True
    )

    print("Priority Result:")
    print(result)