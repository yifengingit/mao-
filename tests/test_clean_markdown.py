from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from clean_markdown import clean_text


class CleanMarkdownTests(unittest.TestCase):
    def test_merges_hard_wrapped_body_lines_but_keeps_paragraph_breaks(self) -> None:
        raw = (
            "第一行正文\n"
            "第二行正文\n"
            "\n"
            "另一段第一行\n"
            "另一段第二行\n"
        )

        self.assertEqual(
            clean_text(raw),
            "第一行正文第二行正文\n\n另一段第一行另一段第二行\n",
        )

    def test_keeps_note_blocks_split(self) -> None:
        raw = (
            "注　　释\n"
            "〔1〕第一行注释\n"
            "第二行注释\n"
            "\n"
            "正文第一行\n"
            "正文第二行\n"
        )

        self.assertEqual(
            clean_text(raw),
            "注　　释\n"
            "〔1〕第一行注释\n"
            "第二行注释\n\n"
            "正文第一行正文第二行\n",
        )

    def test_removes_single_spurious_blank_line_inside_body(self) -> None:
        raw = (
            "第三，选集中作了一些注释。其中一部分是属于题解的，附在各\n"
            "\n"
            "篇第一页的下面；其他部分，有属于政治性质的，有属于技术性质的，都附在文章的末尾。\n"
            "\n"
            "第四，本选集有两种装订的本子。\n"
        )

        self.assertEqual(
            clean_text(raw),
            "第三，选集中作了一些注释。其中一部分是属于题解的，附在各篇第一页的下面；其他部分，有属于政治性质的，有属于技术性质的，都附在文章的末尾。\n\n"
            "第四，本选集有两种装订的本子。\n",
        )

    def test_keeps_date_and_body_separate(self) -> None:
        raw = (
            "（一九二五年十二月一日）\n"
            "谁是我们的敌人？谁是我们的朋友？\n"
        )

        self.assertEqual(
            clean_text(raw),
            "（一九二五年十二月一日）\n谁是我们的敌人？谁是我们的朋友？\n",
        )

    def test_keeps_date_separate_across_blank_line(self) -> None:
        raw = (
            "（一九二五年十二月一日）\n"
            "\n"
            "谁是我们的敌人？谁是我们的朋友？\n"
        )

        self.assertEqual(
            clean_text(raw),
            "（一九二五年十二月一日）\n\n谁是我们的敌人？谁是我们的朋友？\n",
        )

    def test_keeps_short_heading_separate_across_blank_line(self) -> None:
        raw = (
            "贫农说：‘怪不得，年岁大了，明年再还吧！’\n"
            "\n"
            "第四件　推翻土豪劣绅的封建统治\n"
            "——打倒都团\n"
        )

        self.assertEqual(
            clean_text(raw),
            "贫农说：‘怪不得，年岁大了，明年再还吧！’\n\n"
            "第四件　推翻土豪劣绅的封建统治\n——打倒都团\n",
        )

    def test_merges_short_phrase_split_across_blank_line(self) -> None:
        raw = (
            "第一部分是有\n"
            "\n"
            "余钱剩米的，即用其体力或脑力劳动所得，除自给外，每年有余剩。\n"
        )

        self.assertEqual(
            clean_text(raw),
            "第一部分是有余钱剩米的，即用其体力或脑力劳动所得，除自给外，每年有余剩。\n",
        )

    def test_merges_short_word_split_across_blank_line(self) -> None:
        raw = (
            "谭派创\n"
            "\n"
            "始人。谭富英是二十世纪三、四十年代的四大须生之一。\n"
        )

        self.assertEqual(
            clean_text(raw),
            "谭派创始人。谭富英是二十世纪三、四十年代的四大须生之一。\n",
        )

    def test_merges_short_fragment_ending_with_sentence_punctuation(self) -> None:
        raw = (
            "实行坚决\n"
            "\n"
            "抗战！\n"
        )

        self.assertEqual(clean_text(raw), "实行坚决抗战！\n")

    def test_merges_long_line_with_short_sentence_tail(self) -> None:
        raw = (
            "第二十九军的全体爱国将士团结起来，反对妥协退让，实行坚决\n"
            "\n"
            "抗战！\n"
        )

        self.assertEqual(
            clean_text(raw),
            "第二十九军的全体爱国将士团结起来，反对妥协退让，实行坚决抗战！\n",
        )

    def test_merges_long_line_with_short_clause_head(self) -> None:
        raw = (
            "全国军队包括红军在内，拥护蒋介石先生的宣言，反对妥协退\n"
            "\n"
            "让，实行坚决抗战！\n"
        )

        self.assertEqual(
            clean_text(raw),
            "全国军队包括红军在内，拥护蒋介石先生的宣言，反对妥协退让，实行坚决抗战！\n",
        )

    def test_merges_long_line_with_short_noun_tail(self) -> None:
        raw = (
            "（二）全国人民的总动员。开放爱国运动，释放政治犯，取消《危害民国紧急治罪法》〔3〕和《新闻检查条例》〔4〕，承认现有爱国团\n"
            "\n"
            "体的合法地位，扩大爱国团体的组织于工农商学各界。\n"
        )

        self.assertEqual(
            clean_text(raw),
            "（二）全国人民的总动员。开放爱国运动，释放政治犯，取消《危害民国紧急治罪法》〔3〕和《新闻检查条例》〔4〕，承认现有爱国团体的合法地位，扩大爱国团体的组织于工农商学各界。\n",
        )

    def test_merges_long_line_with_short_noun_tail_and_long_following(self) -> None:
        raw = (
            "（二）全国人民的总动员。开放爱国运动，释放政治犯，取消《危害民国紧急治罪法》〔3〕和《新闻检查条例》〔4〕，承认现有爱国团\n"
            "\n"
            "体的合法地位，扩大爱国团体的组织于工农商学各界，武装民众实行自卫，并配合军队作战。\n"
        )

        self.assertEqual(
            clean_text(raw),
            "（二）全国人民的总动员。开放爱国运动，释放政治犯，取消《危害民国紧急治罪法》〔3〕和《新闻检查条例》〔4〕，承认现有爱国团体的合法地位，扩大爱国团体的组织于工农商学各界，武装民众实行自卫，并配合军队作战。\n",
        )

    def test_merges_long_line_with_short_noun_tail_across_two_blank_lines(self) -> None:
        raw = (
            "（二）全国人民的总动员。开放爱国运动，释放政治犯，取消《危害民国紧急治罪法》〔3〕和《新闻检查条例》〔4〕，承认现有爱国团\n"
            "\n"
            "\n"
            "体的合法地位，扩大爱国团体的组织于工农商学各界，武装民众实行自卫，并配合军队作战。\n"
        )

        self.assertEqual(
            clean_text(raw),
            "（二）全国人民的总动员。开放爱国运动，释放政治犯，取消《危害民国紧急治罪法》〔3〕和《新闻检查条例》〔4〕，承认现有爱国团体的合法地位，扩大爱国团体的组织于工农商学各界，武装民众实行自卫，并配合军队作战。\n",
        )

    def test_merges_long_line_with_short_noun_tail_across_three_blank_lines(self) -> None:
        raw = (
            "（二）全国人民的总动员。开放爱国运动，释放政治犯，取消《危害民国紧急治罪法》〔3〕和《新闻检查条例》〔4〕，承认现有爱国团\n"
            "\n"
            "\n"
            "\n"
            "体的合法地位，扩大爱国团体的组织于工农商学各界，武装民众实行自卫，并配合军队作战。\n"
        )

        self.assertEqual(
            clean_text(raw),
            "（二）全国人民的总动员。开放爱国运动，释放政治犯，取消《危害民国紧急治罪法》〔3〕和《新闻检查条例》〔4〕，承认现有爱国团体的合法地位，扩大爱国团体的组织于工农商学各界，武装民众实行自卫，并配合军队作战。\n",
        )

