


def state_changer_monad_example():
    @do(StateChanger)
    def dict_state_copy(key1, key2):
        val = yield dict_state_get(key1)
        yield dict_state_set(key2, val)
        mreturn(val)

    @do(StateChanger)
    def dict_state_get(key, default=None):
        dct = yield get_state()
        val = dct.get(key, default)
        mreturn(val)

    @do(StateChanger)
    def dict_state_set(key, val):
        def dict_set(dct, key, val):
            dct[key] = val
            return dct

        new_state = yield change_state(lambda dct: dict_set(dct, key, val))
        mreturn(val)

    @do(StateChanger)
    def with_dict_state():
        val2 = yield dict_state_set("a", 2)
        yield dict_state_copy("a", "b")
        state = yield get_state()
        mreturn(val2)

    print(with_dict_state().run({}))  # (2, {"a" : 2, "b" : 2})
