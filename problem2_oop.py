from domain.Player import Player


def main():
    code = "b11062ac496663726d930510fb365241"
    problem = 2
    h = 10
    w = 200
    total_day = 1000

    play_p2 = Player(code, problem, h, w, total_day)
    print(play_p2.start())


if __name__ == "__main__":
    main()
