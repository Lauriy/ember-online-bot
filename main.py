from bot import EmberOnline


def main():
    ember = EmberOnline()
    ember.do_init_logic()
    ember.start()


if __name__ == '__main__':
    main()
