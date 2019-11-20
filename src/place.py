import argparse
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

NB_IMAGES = 4

NB_RUNS = 1

THRESHOLD_BETWEEN_IMAGES = 0.1
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
    for _, rectangle in others:
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


def generate_card(
    nb_images,
    rectangles,
    min_size_rec=MIN_SIZE_REC,
    max_size_rec=MAX_SIZE_REC,
    verbose=False,
    return_all=False,
):
    nb_tries = 0
    nb_total_tries = 0

    positions = set()
    real_positions = []
    placed_random_level = []
    placed_rectangles = []

    authorized_random_position = MIN_RANDOM_AUTHORIZED

    while len(rectangles) > 0:
        id_picture, new_rectangle = rectangles.pop()
        if verbose:
            print("format", new_rectangle, authorized_random_position)

        # Contains the center of the rectangle
        position = (
            POSITION_IMAGE_RADIUS
            * math.cos((len(placed_rectangles)) * math.pi * 2.0 / nb_images),
            POSITION_IMAGE_RADIUS
            * math.sin((len(placed_rectangles)) * math.pi * 2.0 / nb_images),
        )
        positions.add(position)
        position += (
            MOVING_RAND_THRESHOLD * authorized_random_position * np.random.random((2,))
        )

        size = max_size_rec
        placed = False
        while size > min_size_rec:
            cur_rect = Rectangle(position, size, new_rectangle)
            if is_available(placed_rectangles, cur_rect) and is_in_circle(cur_rect):
                placed_rectangles.append((id_picture, cur_rect))
                placed_random_level.append(authorized_random_position)
                real_positions.append(position)
                nb_tries = 0
                authorized_random_position = MIN_RANDOM_AUTHORIZED
                if verbose:
                    print("Placed!")
                placed = True
                break
            size -= STEP_SIZE_REC

        if not placed:
            rectangles.append((id_picture, new_rectangle))
            if len(rectangles) == 1:
                nb_tries += 1
            if verbose:
                print("New try")
        if nb_tries % THRESHOLD_FAIL_SINGLE // 10 == (THRESHOLD_FAIL_SINGLE // 10 - 1):
            authorized_random_position *= 1.1
            if verbose:
                print("Increases authorized random", authorized_random_position)

        if nb_tries >= THRESHOLD_FAIL_SINGLE:
            if verbose:
                print("FAILS")
            break

        nb_total_tries += 1
        if nb_total_tries >= THRESHOLD_FAIL_ALL:
            if verbose:
                print("TOTAL FAILS")
            break
        if verbose:
            print()
    if return_all:
        return (real_positions, positions, placed_random_level, placed_rectangles)
    else:
        return {key: val for key, val in placed_rectangles}


def plot_rectangles(real_positions=[], positions=set(), *rects):
    # Create figure and axes
    fig, ax = plt.subplots(1)
    ax.add_patch(patches.Circle((0, 0), 1, facecolor="white", edgecolor="black"))
    for position in real_positions:
        ax.plot([position[0]], [position[1]], marker="o", markersize=2, color="black")
    for position in positions:
        ax.plot([position[0]], [position[1]], marker="o", markersize=1, color="black")
    for i, rectangle in rects:
        # Create a Rectangle patch
        print(rectangle)
        rect = rectangle.get_mpl_rec(i)
        # Add the patch to the Axes
        ax.add_patch(rect)

    plt.xlim(-1.2, 1.2)
    plt.ylim(-1.2, 1.2)
    plt.gca().set_aspect("equal", adjustable="box")
    if NB_RUNS == 1:
        plt.show()
    else:
        plt.savefig("tests/" + str(glob_i) + ".png")
    plt.close()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Run PCA and other clustering algorithms."
    )
    parser.add_argument("nb_runs", type=int, default=1, help="nb of runs", nargs="?")
    args = parser.parse_args()

    NB_RUNS = args.nb_runs

    for glob_i in range(NB_RUNS):
        sizes = np.random.normal(1, 0.5, NB_IMAGES)

        rectangles = list(enumerate(sizes))
        print(rectangles)
        (
            real_positions,
            positions,
            placed_random_level,
            placed_rectangles,
        ) = generate_card(NB_IMAGES, rectangles, return_all=True)

        print("placed_rectangles", placed_rectangles)
        for i, rec in placed_rectangles:
            print(i, rec.size, rec.size * rec.ratio, rec.ratio, COLORS[i % len(COLORS)])
        plot_rectangles(real_positions, positions, *placed_rectangles)
