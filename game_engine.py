FIRST_PLAYER = 0
SECOND_PLAYER = 1
FIRST_PLAYER_SIGN = 'X'
SECOND_PLAYER_SIGN = 'O'
EMPTY_SIGN = "-"

CORRECT_MOVE = 1
WRONG_MOVE = -1


# It's a class which controls all tic-tac-toe game functionalities. The server will use this class to assign
# one engine for each paired players.
class GameEngine:
    def __init__(self, table_size):
        self.table_size = table_size
        self.cur_player = FIRST_PLAYER
        self.table = [[EMPTY_SIGN for i in range(table_size)] for j in range(table_size)]
        self.player_signs = {FIRST_PLAYER: FIRST_PLAYER_SIGN, SECOND_PLAYER: SECOND_PLAYER_SIGN}
        self.win_length = self.initialize_win_length(table_size)
        self.is_draw = -1

    # This function will set win length according to the table_size.
    def initialize_win_length(self, table_size):
        if table_size == 5:
            return 4
        return 3

    # this function will return the game table
    def get_table(self):
        return self.table

    # this function will return the cur active player
    def get_cur_player(self):
        return self.cur_player

    # this function will return the draw flag a flag which specifies whether we have draw or not in the game.
    def get_draw_flag(self):
        return self.is_draw

    # this function checks for the row win condition.
    def check_table_rows(self):
        for row_ind in range(self.table_size):
            for col_ind in range(self.table_size - self.win_length + 1):
                cur_table_part = self.table[row_ind][col_ind:col_ind + self.win_length]
                print(cur_table_part)
                if cur_table_part == [FIRST_PLAYER_SIGN for _ in range(self.win_length)] or \
                        cur_table_part == [SECOND_PLAYER_SIGN for _ in range(self.win_length)]:
                    return True
        return False

    # this function checks for the column win condition.
    def check_table_columns(self):
        for col_ind in range(self.table_size):
            for row_ind in range(self.table_size - self.win_length + 1):
                cur_table_part = []
                for selected_row_ind in range(row_ind, row_ind + self.win_length):
                    cur_table_part.append(self.table[selected_row_ind][col_ind])
                if cur_table_part == [FIRST_PLAYER_SIGN for _ in range(self.win_length)] or \
                        cur_table_part == [SECOND_PLAYER_SIGN for _ in range(self.win_length)]:
                    return True
        return False

    # this function checks for main diagonal win condition.
    def check_table_main_diags(self):
        for col_ind in range(self.table_size):
            for row_ind in range(self.table_size):
                cur_table_part = []
                for offset_value in range(0, self.win_length):
                    if col_ind + offset_value >= self.table_size or row_ind + offset_value >= self.table_size:
                        break
                    cur_table_part.append(self.table[row_ind + offset_value][col_ind + offset_value])
                if cur_table_part == [FIRST_PLAYER_SIGN for _ in range(self.win_length)] or \
                        cur_table_part == [SECOND_PLAYER_SIGN for _ in range(self.win_length)]:
                    return True
        return False

    # this function checks for anti-diagonal win condition
    def check_table_anti_diags(self):
        for col_ind in range(self.table_size):
            for row_ind in range(self.table_size):
                cur_table_part = []
                for offset_value in range(0, self.win_length):
                    if col_ind - offset_value < 0 or row_ind + offset_value >= self.table_size:
                        break
                    cur_table_part.append(self.table[row_ind + offset_value][col_ind - offset_value])
                if cur_table_part == [FIRST_PLAYER_SIGN for _ in range(self.win_length)] or \
                        cur_table_part == [SECOND_PLAYER_SIGN for _ in range(self.win_length)]:
                    return True
        return False

    # this function, checks that whether the table is full or not.
    def check_table_draw(self):
        for row_ind in range(self.table_size):
            for col_ind in range(self.table_size):
                if self.table[row_ind][col_ind] == EMPTY_SIGN:
                    return False
        return True

    # this function will use all types of win condition functions which we described before to
    # check whether the game has finished or not.
    def is_game_finished(self):
        row_finish_flag = self.check_table_rows()
        column_finish_flag = self.check_table_columns()
        main_diag_finish_flag = self.check_table_main_diags()
        anti_diag_finish_flag = self.check_table_anti_diags()
        if row_finish_flag is False and column_finish_flag is False and \
                main_diag_finish_flag is False and anti_diag_finish_flag is False:
            self.is_draw = self.check_table_draw()
        return row_finish_flag or column_finish_flag or main_diag_finish_flag or anti_diag_finish_flag or self.is_draw

    # this function will change the active player
    def update_active_player(self):
        if self.cur_player == FIRST_PLAYER:
            self.cur_player = SECOND_PLAYER
        else:
            self.cur_player = FIRST_PLAYER

    # this function will update the table according to the active plyer movement. It also checks
    # whether the player move is wrong or not.
    def update_table(self, mark_position):
        if mark_position >= self.table_size * self.table_size:
            return self.table, WRONG_MOVE
        ind1 = mark_position // self.table_size
        ind2 = mark_position % self.table_size
        if self.table[ind1][ind2] != EMPTY_SIGN:
            return self.table, WRONG_MOVE
        self.table[ind1][ind2] = self.player_signs[self.get_cur_player()]
        return self.table, CORRECT_MOVE
