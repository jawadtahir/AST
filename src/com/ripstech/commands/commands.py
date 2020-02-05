'''
Created on Feb 4, 2020

@author: foobar
'''
import json

BREAK_TOKENS = ["SELECT", "FROM", "WHERE",
                "ORDER", "INSERT", "INTO", "VALUES", "DELETE"]

LOGICAL_TOKENS = ["AND", "OR"]


def resolve_conditions(cond_tkns):
    ret_val = []

    if len(cond_tkns) == 0:
        return []

    cur_cond = []
    while len(cond_tkns) > 0:
        cur_tkn = cond_tkns.pop(0)
        if cur_tkn in LOGICAL_TOKENS:
            ret_val.append(Condition(cur_cond))
            cur_cond = ""
        else:
            cur_cond.append(cur_tkn)

    ret_val.append(Condition(cur_cond))

    return ret_val


class Condition(object):
    def __init__(self, con_arr):
        self.lhs = con_arr.pop(0)
        self.rhs = con_arr.pop()
        self.operand = " ".join(con_arr)


class Commands(object):
    def __init__(self, command_str):
        self.parse(command_str)

    def print_ast(self):
        print(json.dumps(self, default=lambda o: o.__dict__,
                         sort_keys=False, indent=4))


class USE(Commands):
    def parse(self, command_str):
        cmd_tkns = [tkn.upper().strip() for tkn in command_str.split(" ")]
        self.type = cmd_tkns.pop(0)
        self.database = cmd_tkns.pop(0)


class SELECT(Commands):
    def parse(self, command_str):
        cmd_tkns = [tkn.upper().strip() for tkn in command_str.split(" ")]

        cols = []
        table = ""
        conditions = []
        opts = []

        curr_tkn = cmd_tkns.pop(0)
        self.type = curr_tkn

        try:
            curr_tkn = cmd_tkns.pop(0)
            while not curr_tkn in BREAK_TOKENS:
                cols.append(curr_tkn.replace(",", ""))
                curr_tkn = cmd_tkns.pop(0)

            curr_tkn = cmd_tkns.pop(0)
            table = curr_tkn

            if len(cmd_tkns) > 0:
                curr_tkn = cmd_tkns.pop(0)
                if curr_tkn == "WHERE":
                    curr_tkn = cmd_tkns.pop(0)
                    while not curr_tkn in BREAK_TOKENS:
                        conditions.append(curr_tkn)
                        curr_tkn = cmd_tkns.pop(0)
                if curr_tkn == "ORDER":
                    curr_tkn = cmd_tkns.pop(0)
                    curr_tkn = cmd_tkns.pop(0)
                    while not curr_tkn in BREAK_TOKENS:
                        opts.append(curr_tkn.replace(",", ""))
                        curr_tkn = cmd_tkns.pop(0)

        except IndexError:
            pass

        self.columns = cols if len(cols) > 0 else ["*"]
        self.table = table if len(table) > 0 else "*"
        self.conditions = resolve_conditions(conditions)
        self.opts = opts if len(opts) > 0 else []


class INSERT(Commands):
    def parse(self, command_str):
        cmd_tkns = [tkn.upper().strip() for tkn in command_str.split(" ")]

        curr_tkn = cmd_tkns.pop(0)
        self.type = curr_tkn
        cmd_tkns.pop(0)
        curr_tkn = cmd_tkns.pop(0)
        table = curr_tkn
        command_str = command_str.upper()

        col_index = command_str.find(table)
        col_index += len(table)

        val_index = command_str.find("VALUES")

        col_str = command_str[col_index: val_index]
        val_str = command_str[val_index + 6:]

        col_str = col_str.strip()
        val_str = val_str.strip()

        if len(col_str) > 1:
            col_str = col_str[1:len(col_str) - 2]
        val_str = val_str[1:len(val_str) - 2]

        cols = [col.strip() for col in col_str.split(",")]
        vals = [val.strip() for val in val_str.split(",")]

        self.table = table
        self.columns = cols if len(cols) > 0 else ["*"]
        self.values = vals if len(vals) > 0 else []


class DELETE(Commands):
    def parse(self, command_str):
        cmd_tkns = [tkn.upper().strip() for tkn in command_str.split(" ")]

        table = ""
        conditions = []

        curr_tkn = cmd_tkns.pop(0)
        self.type = curr_tkn
        cmd_tkns.pop(0)
        curr_tkn = cmd_tkns.pop(0)
        table = curr_tkn
        try:
            curr_tkn = cmd_tkns.pop(0)
            curr_tkn = cmd_tkns.pop(0)
            while not curr_tkn in BREAK_TOKENS:
                conditions.append(curr_tkn)
                curr_tkn = cmd_tkns.pop(0)

        except IndexError:
            pass

        self.table = table
        self.conditions = resolve_conditions(conditions)


class CommandFactory(object):
    '''
    CommandFactory to initialize commands
    '''

    @staticmethod
    def get_command(command_str):
        '''
        Static factory method
        '''
        command_str = command_str.replace(";", "")

        cmd_tkns = command_str.split(" ")
        cmd_typ = cmd_tkns[0].strip()

        if cmd_typ.upper() == "USE":
            return USE(command_str)
        elif cmd_typ.upper() == "SELECT":
            return SELECT(command_str)
        elif cmd_typ.upper() == "INSERT":
            return INSERT(command_str)
        elif cmd_typ.upper() == "DELETE":
            return DELETE(command_str)
        else:
            raise SyntaxError("Malformed command")


if __name__ == "__main__":
    com_str = r"INSERT INTO user_notes (id, user_id, note, created) VALUES (1, 1, \"Note 1\", NOW());"
    com = CommandFactory.get_command(com_str)
    com.print_ast()
