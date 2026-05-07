from shelby.safety import classify_command, RiskLevel

def test_safety():
    assert classify_command("ls -la") == RiskLevel.SAFE
    assert classify_command("rm file.txt") == RiskLevel.CAUTION
    assert classify_command("rm -rf /") == RiskLevel.DANGER
    assert classify_command("pip install requests") == RiskLevel.CAUTION
    assert classify_command("git log") == RiskLevel.SAFE
    assert classify_command("DROP TABLE users") == RiskLevel.DANGER
    print("Safety tests passed!")

if __name__ == "__main__":
    test_safety()
