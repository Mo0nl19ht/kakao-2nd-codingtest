from domain.Player import Player


def main():
    code = "b11062ac496663726d930510fb365241"
    problem = 1
    h = 3
    w = 20
    total_day = 200

    play_p1 = Player(code, problem, h, w, total_day)
    print(play_p1.start())


if __name__ == "__main__":
    main()
