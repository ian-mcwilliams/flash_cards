# -*- coding: utf-8 -*-
import random
import re
import collections


def ordic(contents=[]):
    return collections.OrderedDict(contents)


def flash_cards():
    print ''
    print '============================='
    print '======== FLASH CARDS ========'
    print '============================='
    print ''
    quit_app = False
    while not quit_app:
        quit_app = start_session()
    print 'goodbye!'


def start_session():
    run_type = raw_input('revise (r), learn(l), play (p) or quit(q)? ')
    if run_type not in ('r', 'p', 'l', 'q'):
        print 'that is not a valid selection!'
        return False
    if run_type == 'q':
        return True
    card_sets = get_flash_cards_data_set_names()
    print 'available word sets:'
    print ''
    for card_set in card_sets:
        print card_set
    print ''
    valid_word_set = False
    while not valid_word_set:
        word_list = raw_input('choose a list by letter: ')
        words = get_words(word_list)
        if words:
            valid_word_set = True
        else:
            print 'that is not a valid selection!'
    if run_type == 'r':
        revise_words(words)
    elif run_type == 'p':
        set_up_game(words)
    elif run_type == 'l':
        prepare_learning(words)
    print ''
    return False


def revise_words(words):
    print ''
    print 'text in square brackets is for info and should be excluded from answers you give'
    for (english_word, french_word) in words.items():
        english = '/'.join(english_word) if type(english_word) == tuple else english_word
        english += (39 - len(english)) * ' '
        french = '/'.join(french_word) if type(french_word) == tuple else french_word
        print ''
        print english, french


def prepare_learning(words):
    print ''
    print 'this group contains', len(words.keys()), 'words'
    group_size = input('how many do you want to learn? ')
    print ''
    print 'revise until you know them all'
    print 'keep answering the same', group_size, 'translations in runs of 20 questions until you know them by heart!'
    print_rules()

    replay = True
    new_sample = True

    while replay:
        if new_sample:
            sample_dict = ordic([])
            for i in xrange(group_size):
                key = random.choice(words.keys())
                sample_dict[key] = words[key]
                del words[key]
            revise_words(sample_dict)

        test_words(sample_dict, 20)
        replay_answer = None
        print ''
        while replay_answer not in ('c', 'n', 'r'):
            replay_answer = raw_input('do you want to continue with these words (c), get a new set of words from this group (n), or return to the main menu (r)? ')
        if replay_answer == 'r':
            replay = False
        elif replay_answer == 'c':
            new_sample = False
        elif replay_answer == 'n':
            new_sample = True


def set_up_game(words):
    rounds = len(words.keys()) * 2
    print ''
    print 'play the flash card game!'
    print 'there will be', rounds, 'rounds'
    print 'get all translations right to win!'

    correct_count = test_words(words, rounds)
    if not correct_count:
        correct_count = 0

    print 'game over!'
    print 'you got', correct_count, 'right, and', rounds - correct_count, 'wrong'

    if correct_count == rounds:
        print 'you got them all right, amazing!'
    else:
        print 'keep trying and get them all right!'
    print ''


def print_rules():
    print ''
    print 'for a and e, follow with \\ or / to show the grave or accent (à, á, è, é)'
    print 'for a, e, i, o and u, follow with ^ to show the circumflex (â, ê, î, ô, û)'
    print 'for c, follow with ? to show the cedille (ç)'
    print 'for i, follow with : for the trema (ï)'
    print 'for o, follow with £ for the ligature of o and e (œ)'
    print ''
    print 'if multiple cases apply they will all be shown, but either is considered a correct answer!'


def test_words(all_words, rounds):
    words = ordic(all_words)
    correct_count = 0
    print ''
    print 'enter q to quit before the end'
    print ''
    for i in xrange(rounds):
        english_word = random.choice(words.keys())
        french_word = words[english_word]
        word_pair = [english_word, french_word]
        random.shuffle(word_pair)
        word, translation = word_pair

        print ''.join(['word number ', str(i + 1), ': ', stringify_word(word)])
        response = raw_input('what is the translation? ')
        if response == 'q':
            return False
        filtered_response = resolve_diacritics(response)
        filtered_translation = filter_translation(translation)

        if check_response(filtered_response, filtered_translation):
            print filtered_response, 'is correct!'
            correct_count += 1
        else:
            if type(filtered_translation) is tuple:
                answers = []
                for item in filtered_translation:
                    if item[0] != '[':
                        answers.append(item)
                filtered_translation = ' or '.join(answers)
            print filtered_response, 'is not correct, the right translation is', filtered_translation

        del words[english_word]
        if len(words.keys()) == 0:
            words.update(all_words)
        print ''
    return correct_count


def stringify_word(input_var):
    if type(input_var) is tuple:
        return ', '.join(input_var)
    return input_var


def check_response(response, translation):
    if response == translation or type(translation) == tuple and response in translation:
        return True
    else:
        return False


def filter_translation(translation):
    if type(translation) is tuple:
        filtered_translation = []
        for instance in translation:
            filtered_translation.append(execute_filter(instance))
        return tuple(filtered_translation)
    else:
        return execute_filter(translation)


def execute_filter(translation):
    comment_index = translation.find(" [", 0)
    if comment_index >= 0:
        return translation[:comment_index]
    else:
        return translation


def resolve_diacritics(raw_str):
    processed_str = ''
    diacritic_mark = False
    special_chars = 0
    regex = re.compile("[a-z]")
    for i in xrange(len(raw_str)):
        current_letter = raw_str[i]
        if diacritic_mark:
            special_chars += 1
            diacritic_mark = False
        elif regex.match(current_letter):
            if i < len(raw_str) - 1:
                next_letter = raw_str[i + 1]
                diacritic = get_diacritic(current_letter, next_letter)
                if diacritic != current_letter:
                    diacritic_mark = True
                processed_str += diacritic
            else:
                processed_str += current_letter
        else:
            processed_str += current_letter
    return processed_str


def get_diacritic(letter, next_letter):
    if letter == 'a':
        if next_letter == '\\':
            return 'à'
        elif next_letter == '/':
            return 'á'
        elif next_letter == '^':
            return 'â'
    elif letter == 'c':
        if next_letter == '?':
            return 'ç'
    elif letter == 'e':
        if next_letter == '\\':
            return 'è'
        elif next_letter == '/':
            return 'é'
        elif next_letter == '^':
            return 'ê'
    elif letter == 'i':
        if next_letter == '^':
            return 'î'
        if next_letter == ':':
            return 'ï'
    elif letter == 'o':
        if next_letter == '£':
            return 'œ'
        elif next_letter == '^':
            return 'ô'
    elif letter == 'u':
        if next_letter == '^':
            return 'û'
    return letter


def get_words(word_list):
    print ''.join(['you have selected word group ', word_list, '!'])
    all_lists = get_flash_cards_data()
    return_val = all_lists[word_list] if word_list in all_lists.keys() else None
    return return_val


# -*- coding: utf-8 -*-


def get_flash_cards_data_set_names():
    return [
        'a: duration adverbs',
        'b: personality adjectives',
        'c: passé composé, être verbs',
        'd: family',
        'e: house',
        'f: clothing',
        'g: hobbies',
        'h: times',
        'i: numbers',
        'j: stressed pronouns',
        'k: possessive adjectives',
        'l: possessive pronouns',
        'm: imparfait/passé composé exercise I',
        'n: imparfait/passé composé exercise II'
    ]


def get_flash_cards_data():
    return ordic([('a', ordic([
        ('during',	                                'pendant'),
        ('childhood',	                            'enfance'),
        ('always',	                                'toujours'),
        ('often',	                                'souvent'),
        ('a lot',	                                'beaucoup'),
        ('regularly',	                            'regulierement'),
        ('to know',	                                'savoir'),
        ])), ('b', ordic([
            ('personality',                             'caractère'),
            ('athletic',	                            'sportif'),
            ('brave',	                                'courageux'),
            (('cunning', 'shrewd'),	                    'malin'),
            ('friendly',     	                        'amical'),
            ('funny',	                                'drôle'),
            ('hard-working',	                        'travailleur'),
            ('interesting',	                            'intéressant'),
            ('kind',	                                'gentil'),
            ('nice',	                                ('sympa', 'sympatique')),
            ('cowardly',	                            'lâche'),
            ('unfriendly',	                            'froid'),
            ('serious',	                                'sérieux'),
            ('lazy',	                                'paresseux'),
            ('boring',	                                'ennuyeux'),
            ('mean',	                                'méchant'),
            ('open-minded',                             'sans préjugés'),
            ('outgoing',                                'ouvert'),
            ('patient',                                 'patient'),
            ('patriotic',                               'patriotique'),
            ('smart',                                   'intelligent'),
            ('sophisticated',                           'raffiné'),
            ('strong',                                  'fort'),
            ('studious',                                'studieux'),
            ('snobbish',                                'snob'),
            ('shy',                                     'timide'),
            ('impatient',                               'impatient'),
            ('stupid',                                  'stupide'),
            ('naive',                                   'naïf'),
            ('weak',                                    'faible'),
            ('playful',                                 'taquin'),
        ])), ('c', ordic([
            ('to go down',                              'descendre'),
            ('to remain',                               'restir'),
            ('to die',                                  'mourir'),
            ('to return',                               'retourner'),
            ('to go out',                               'sortir'),
            ('to come',                                 'venir'),
            ('to arrive',                               'arriver'),
            ('to be born',                              'naître'),
            ('to become',                               'devinir'),
            ('to enter',                                'entrer'),
            ('to return [home]',                        'rentrer'),
            ('to fall',                                 'tomber'),
            ('to come back',                            'revenir'),
            ('to go',                                   'aller'),
            ('to go up',                                'monter'),
            ('to leave',                                'partir'),
            ('to pass by',                              'passer'),
        ])), ('d', ordic([
            ('family',                                  'la famille'),
            ('father',                                  'un père'),
            ('mother',                                  'une mère'),
            ('brother',                                 'un frère'),
            ('sister',                                  'une sœur'),
            ('son',                                     'un fils'),
            ('daughter',                                'une fille'),
            ('husband',                                 'un mari'),
            ('wife',                                    'une femme'),
            ('grandfather',                             'un grand-père'),
            ('grandmother',                             'une grand-mére'),
            ('grandson',                                'un petit-fils'),
            ('granddaughter',                           'une petit-fille'),
            ('cousin [male]',                           'un cousin'),
            ('cousin [female]',                         'une cousine'),
            ('uncle',                                   'un oncle'),
            ('aunt',                                    'une tante'),
            ('nephew',                                  'un neveu'),
            ('niece',                                   'une nièce'),
        ])), ('e', ordic([
            ('house',                                   'la maison'),
            (('office', 'study'),                       'le bureau de travail'),
            ('bedroom',                                 'la chambre (à coucher)'),
            ('kitchen',                                 'la cuisine'),
            ('hall',                                    "l'entrèe"),
            ('stairs',                                  "l'escalier"),
            ('attic',                                   'le grenier'),
            ('garden',                                  'le jardin'),
            ('a room',                                  ('une pièce', 'une salle')),
            (('bathroom', 'washroom'),                  'la salle de bains'),
            ('dining room',                             'la salle à manger'),
            ('living room',                             'le salon'),
            ('toilet',                                  'les toilettes'),
        ])), ('f', ordic([
            ('clothing',                                'les vêtements'),
            ('coat',                                    'un manteau'),
            ('jacket',                                  'un blouson'),
            ('sweater',                                 'un pull'),
            ('t-shirt',                                 'un tee-shirt'),
            ('trousers',                                'un pantalon'),
            ('jeans',                                   'un jean'),
            ('bathing suit',                            'un maillot (de bain)'),
            ('shorts',                                  'un short'),
            ('socks',                                   'des chaussettes [f]'),
            ('shoes',                                   'des chaussures [f]'),
            ('trainers',                                'des baskets [m]'),
            ('boots',                                   'des bottes [f]'),
            ('sandals',                                 'des sandales [f]'),
            ('pyjamas',                                 'un pyjama'),
            ('suit',                                    'un costume'),
        ])), ('g', ordic([
            ('hobbies',                                 'loisirs'),
            ('basketball',                              'le basket'),
            ('biking',                                  ('le cyclisme', 'le vélo')),
            ('chess',                                   'les échecs'),
            ('cooking',                                 'la cuisine'),
            ('dancing',                                 'la danse'),
            ('fishing',                                 'la pêche'),
            ('football',                                'le football'),
            ('gardening',                               'le jardinage'),
            ('hiking',                                  'la randonnée'),
            ('hockey',                                  'le hockey'),
            ('hunting',                                 'la chasse'),
            ('jogging',                                 'le jogging'),
            ('a movie',                                 'un film'),
            ('music',                                   'la musique'),
            ('reading',                                 'la lecture'),
            ('sailing',                                 'la voile'),
            ('skiing',                                  'le ski'),
            ('soccer',                                  ('le football', 'le foot')),
            ('swimming',                                'la natation'),
            (('television', 'TV'),                      ('la télévision', 'la télé')),
            ('tennis',                                  'le tennis'),
            ('toys',                                    'les jouets')
        ])), ('h', ordic([
            ('seasons',                                 'saisons'),
            ('winter',                                  'hiver'),
            ('spring',                                  'printemps'),
            ('summer',                                  'été'),
            ('autumn',                                  'automne [pronounced oton]'),
            ('morning',                                 'matin'),
            ('afternoon',                               'aprés-midi'),
            ('evening',                                 'soir'),
            ('months',                                  'mois [not numbers]'),
            ('january',                                 'janvier'),
            ('february',                                'fevrier'),
            ('march',                                   'mars [pronounced mars]'),
            ('april',                                   'avril'),
            ('may',                                     'mai'),
            ('june',                                    'juin'),
            ('july',                                    'juillet'),
            ('august',                                  'août'),
            ('september',                               'septembre'),
            ('october',                                 'octobre'),
            ('november',                                'novembre'),
            ('december',                                'décembre'),
        ])), ('i', ordic([
            ('numbers',                                 'mois [not months]'),
            ('one',                                     'un'),
            ('two',                                     'deux'),
            ('three',                                   'trois'),
            ('four',                                    'quatre'),
            ('five',                                    'cinq'),
            ('six',                                     'six'),
            ('seven',                                   'sept'),
            ('eight',                                   'huit'),
            ('nine',                                    'nouf'),
            ('ten',                                     'dix'),
            ('eleven',                                  'onze'),
            ('twelve',                                  'douze'),
            ('thirteen',                                'treize'),
            ('fourteen',                                'quatorze'),
            ('fifteen',                                 'quinze'),
            ('sixteen',                                 'seize'),
            ('seventeen',                               'dix-sept'),
            ('eighteen',                                'dix-huit'),
            ('nineteen',                                'dix-nouf'),
            ('twenty',                                  'vingt'),
            ('twenty one',                              'vingt-et-un'),
            ('twenty two',                              'vingt-deux'),
            ('thirty',                                  'trente'),
            ('forty',                                   'quarante'),
            ('fifty',                                   'cinquante'),
            ('sixty',                                   'soixante'),
            ('seventy',                                 'soixante-dix'),
            ('seventy one',                             'soixante-et-onze'),
            ('seventy two',                             'soixante-douze'),
            ('eighty',                                  'quatre-vingts'),
            ('eight one',                               'quatre-vingt-un'),
            ('ninety nine',                             'quatre-vingt-dix-nouf'),
            ('one hundred',                             'cent')
        ])), ('j', ordic([
            ('me',                                      'moi'),
            ('you',                                     'toi'),
            ('him',                                     'lui'),
            ('her',                                     'elle'),
            ('oneself',                                 'soi'),
            ('us',                                      'nous'),
            ('you [plural]',                            'vous'),
            ('them [m]',                                'eux'),
            ('them [f]',                                'elles'),
        ])), ('k', ordic([
            ('my [m]',                                  'mon'),
            ('my [f]',                                  'ma'),
            ('my [before vowel]',                       'mon'),
            ('my [plural]',                             'mes'),
            ('your [inf, m]',                           'ton'),
            ('your [inf, f]',                           'ta'),
            ('your [inf, before vowel]',                'ton'),
            ('your [inf, p]',                           'tes'),
            (('his', 'her', 'its', '[m]'),              'son'),
            (('his', 'her', 'its', '[f]'),              'sa'),
            (('his', 'her', 'its', '[before vowel]'),   'son'),
            (('his', 'her', 'its', '[p]'),              'ses'),
            ('our [m]',                                 'notre [m]'),
            ('our [f]',                                 'notre [f]'),
            ('our [before vowel]',                      'notre [before vowel]'),
            ('our [p]',                                 'nos'),
            ('your [for m]',                            'votre [m]'),
            ('your [for f]',                            'votre [f]'),
            ('your [for before vowel]',                 'votre [before vowel]'),
            ('your [for p]',                            'vos'),
            ('their [m]',                               'leur'),
            ('their [f]',                               'leur'),
            ('their [before vowel]',                    'leur'),
            ('their [p]',                               'leurs'),
        ])), ('l', ordic([
            ('mine [m s]',                              'le mien'),
            ('mine [f s]',                              'la mienne'),
            ('mine [m p]',                              'les miens'),
            ('mine [f p]',                              'les miennes'),
            ('yours [inf m s]',                         'le tien'),
            ('yours [inf f s]',                         'la tienne'),
            ('yours [inf m p]',                         'les tiens'),
            ('yours [inf f p]',                         'les tiennes'),
            (('his', 'hers', 'its', '[m s]'),           'le sien'),
            (('his', 'hers', 'its', '[f s]'),           'la sienne'),
            (('his', 'hers', 'its', '[m p]'),           'les siens'),
            (('his', 'hers', 'its', '[f p]'),           'les siennes'),
            ('ours [m s]',                              'le nôtre'),
            ('ours [f s]',                              'la nôtre'),
            ('ours [m p]',                              'les nôtres [m]'),
            ('ours [f p]',                              'les nôtres [f]'),
            ('yours [for m s]',                         'le vôtre'),
            ('yours [for f s]',                         'la vôtre'),
            ('yours [for m p]',                         'les vôtres [m]'),
            ('yours [for f p]',                         'les vôtres [f]'),
            ('theirs [m s]',                            'le leur'),
            ('theirs [f s]',                            'la leur'),
            ('theirs [m p]',                            'les leurs'),
            ('theirs [f p]',                            'les leurs'),
        ])), ('m', ordic([
            ('last',                                    'dernier'),
            ('invite',                                  'inviter'),
            ('desire',                                  'envie'),
            ('leave',                                   'partir'),
            ('because',                                 'parce que'),
            ('to arrive',                               'arriver'),
            ('after',                                   'après'),
            ('other',                                   'autre'),
            ('to know',                                 'connaître'),
            ('neighbourhood',                           'quartier'),
            ('but',                                     'mais'),
            (('to manage', 'to achieve'),               'réussir à'),
            ('find',                                    'trouver'),
            ('to sing',                                 'chanter'),
            ('around',                                  'autour'),
        ])), ('n', ordic([
            ('yesterday',                               'hier'),
            ('to get up',                               'lever'),
            ('the weather is good',                     'il fait beau'),
            ('very',                                    'très'),
            ('outside',                                 'dehors'),
            ('go for a walk',                           'promenade'),
            ('to call',                                 'téléphoner'),
            ('unfortunately',                           'malheureusemen'),
            ('at',                                      'chez'),
            ('to take',                                 'prendre'),
            ('cap',                                     'casquette'),
            ('with',                                    'avec'),
            ('dog',                                     'chien'),
            ('there is',                                'il y a'),
            ('people',                                  'gens'),
            ('a lot',                                   'beaucoup'),
            ('youths',                                  'des jeunes'),
            (('in love', 'lover'),                      'amoureux'),
            ('shadow',                                  'ombre'),
            ('trees',                                   'arbres'),
            ('underneath',                              'sous'),
            ('slowly',                                  'lentement'),
            ('near',                                    'près de'),
            ('lake',                                    'lac'),
            ('to see',                                  'voir'),
            ('woman',                                   'femme'),
            ('say',                                     'dire'),
            ('lunch',                                   'déjeuner'),
            (('to accept', 'to say yes'),               'répondre à l\'affirmatif'),
            ('together',                                'ensemble'),
            ('to be hungry',                            'avoir faim'),
            ('to order',                                'commander'),
        ])), ('n', ordic([
            ('to have fun',                             's\'amuser'),
            ('to get up',                               'se lever'),
            ('to wash oneself',                         'se laver'),
            ('to hurry',                                'se dépêcher'),
            ('to comb',                                 'se peigner'),
            ('to get dressed',                          's\'habiller'),
            ('to get married',                          'se marier'),
            ('to rest',                                 'se reposer'),
            ('to remember',                             'se souvenir de'),
            ('to get along well',                       's\'entendre bien'),
            ('to go to bed',                            'se coucher'),
            ('to brush',                                'se brosser'),
            ('to put on make up',                       'se maquiller'),
            ('to break [arm, leg etc]',                 'se casser'),
            ('to wake up',                              'se réveiller'),
            ('to shave',                                'se raser'),
            ('to get bored',                            's\'ennuyer'),
            ('to take a walk',                          'se promener'),
            ('to be interested in',                     's\'intéresser à'),
            (('to train', 'to practise'),               's\'entraîner'),
            ('to relax',                                'se détendre'),
        ]))])


flash_cards()