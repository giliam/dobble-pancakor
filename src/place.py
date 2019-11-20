import argparse
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

parser = argparse.ArgumentParser(description="Run PCA and other clustering algorithms.")
parser.add_argument("nb_runs", type=int, default=1, help="nb of runs", nargs="?")
args = parser.parse_args()

NB_RUNS = args.nb_runs

NB_IMAGES = 7


THRESHOLD_BETWEEN_IMAGES = 0.05
MIN_SIZE_REC = 0.25 * math.sqrt(math.pi * 1 * 1 / NB_IMAGES)
MAX_SIZE_REC = 0.7 * math.sqrt(math.pi * 1 * 1 / NB_IMAGES)
STEP_SIZE_REC = 0.025
POSITION_IMAGE_RADIUS = 0.55

MOVING_RAND_THRESHOLD = 0.9

THRESHOLD_FAIL_SINGLE = 500
THRESHOLD_FAIL_ALL = 10000

MIN_RANDOM_AUTHORIZED = 0.1

COLORS = ["r", "b", "g", "orange", "yellow", "purple", "pink"]


class Rectangle:
    def __init__(self, pos, size, ratio):
        self.pos = pos
        self.size = size
        self.ratio = ratio

    def get_mpl_rec(self, i):
        return patches.Rectangle(
            (self.pos[0] - self.size / 2.0, self.pos[1] - self.size * self.ratio / 2.0),
            self.size,
            self.size * self.ratio,
            linewidth=1,
            edgecolor=COLORS[i % len(COLORS)],
            facecolor="none",
        )

    def __str__(self):
        return f"Rectangle(pos=({self.pos[0]},{self.pos[1]}), size={self.size}, ratio={self.ratio})"

    def __repr__(self):
        return self.__str__()


def dist(p1, p2):
    return abs(p1[0] - p2[0]), abs(p1[1] - p2[1])


def dist_center(pos):
    return math.sqrt(pos[0] * pos[0] + pos[1] * pos[1])


def test_intersection(rec_1, rec_2):
    dist_x, dist_y = dist(rec_1.pos, rec_2.pos)
    if dist_x > rec_1.size / 2.0 + rec_2.size / 2.0 + THRESHOLD_BETWEEN_IMAGES:
        return False
    elif (
        dist_y
        > rec_1.size * rec_1.ratio / 2.0
        + rec_2.size * rec_2.ratio / 2.0
        + THRESHOLD_BETWEEN_IMAGES
    ):
        return False
    return True


def is_available(others, current_rec):
    for rectangle in others:
        if test_intersection(rectangle, current_rec):
            return False
    return True


def is_in_circle(rec):
    p1 = rec.pos + rec.size / 2.0 * np.array((1.0, rec.ratio))
    p2 = rec.pos + rec.size / 2.0 * np.array((1.0, -1.0 * rec.ratio))
    p3 = rec.pos + rec.size / 2.0 * np.array((-1.0, rec.ratio))
    p4 = rec.pos + rec.size / 2.0 * np.array((-1.0, -1.0 * rec.ratio))
    return (
        dist_center(p1) < 1
        and dist_center(p2) < 1
        and dist_center(p3) < 1
        and dist_center(p4) < 1
    )


def generate(rectangles):
    nb_tries = 0
    nb_total_tries = 0

    positions = set()
    real_positions = []
    placed_random_level = []
    placed_rectangles = []

    authorized_random_position = MIN_RANDOM_AUTHORIZED

    while len(rectangles) > 0:
        new_rectangle = rectangles.pop()
        print("format", new_rectangle, authorized_random_position)

        position = (
            POSITION_IMAGE_RADIUS
            * math.cos((len(placed_rectangles)) * math.pi * 2.0 / NB_IMAGES),
            POSITION_IMAGE_RADIUS
            * math.sin((len(placed_rectangles)) * math.pi * 2.0 / NB_IMAGES),
        )
        positions.add(position)
        position += (
            MOVING_RAND_THRESHOLD * authorized_random_position * np.random.random((2,))
        )

        size = MAX_SIZE_REC
        placed = False
        while size > MIN_SIZE_REC:
            cur_rect = Rectangle(position, size, new_rectangle)
            if is_available(placed_rectangles, cur_rect) and is_in_circle(cur_rect):
                placed_rectangles.append(cur_rect)
                placed_random_level.append(authorized_random_position)
                real_positions.append(position)
                nb_tries = 0
                authorized_random_position = MIN_RANDOM_AUTHORIZED
                print("Placed!")
                placed = True
                break
            size -= STEP_SIZE_REC

        if not placed:
            rectangles.append(new_rectangle)
            if len(rectangles) == 1:
                nb_tries += 1
            print("New try")
        if nb_tries % THRESHOLD_FAIL_SINGLE // 10 == (THRESHOLD_FAIL_SINGLE // 10 - 1):
            authorized_random_position *= 1.1
            print("Increases authorized random", authorized_random_position)

        if nb_tries >= THRESHOLD_FAIL_SINGLE:
            print("FAILS")
            break

        nb_total_tries += 1
        if nb_total_tries >= THRESHOLD_FAIL_ALL:
            print("TOTAL FAILS")
            break
        print()
    return real_positions, positions, placed_random_level, placed_rectangles


def plot_rectangles(real_positions=[], positions=set(), *rects):
    # Create figure and axes
    fig, ax = plt.subplots(1)
    ax.add_patch(patches.Circle((0, 0), 1))
    for position in real_positions:
        print(position[0])
        ax.plot([position[0]], [position[1]], marker="o", markersize=2, color="black")
    for position in positions:
        ax.plot([position[0]], [position[1]], marker="o", markersize=1, color="black")
    for i, rectangle in enumerate(rects):
        # Create a Rectangle patch
        rect = rectangle.get_mpl_rec(i)
        print(rect)
        # Add the patch to the Axes
        ax.add_patch(rect)

    plt.xlim(-1.2, 1.2)
    plt.ylim(-1.2, 1.2)
    if NB_RUNS == 1:
        plt.show()
    else:
        plt.savefig("tests/" + str(glob_i) + ".png")
    plt.close()


for glob_i in range(NB_RUNS):
    sizes = np.random.normal(1, 0.25, NB_IMAGES)

    rectangles = list(sizes)
    real_positions, positions, placed_random_level, placed_rectangles = generate(
        rectangles
    )

    print("positions", positions)
    print("placed_random_level", placed_random_level)
    print("placed_rectangles", placed_rectangles)
    plot_rectangles(real_positions, positions, *placed_rectangles)
