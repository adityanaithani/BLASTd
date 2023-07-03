import discord
from discord.ext import commands
from decouple import config
from Bio.Seq import Seq
from Bio import SeqIO
from Bio.Alphabet import generic_dna
from Bio.Blast import NCBIWWW, NCBIXML

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print("Logged in as {0.user}".format(bot))
    channel = bot.get_channel(1063999449204011088)
    await channel.send("BLASTd logged in!")


# test command
@bot.command()
async def test(ctx, *, arg):
    await ctx.send(arg)


@bot.command()
async def blastn(ctx, arg):  # run a blastn (nucleotide -> nucleotide)
    # get gene sequence from message
    sequence = arg
    # validate the input sequence
    try:
        valid_sequence = Seq(sequence, generic_dna)
    except:
        await ctx.send("DNA sequence invalid. Please try again!")
        return

    # run a BLAST search using the sequence
    blast_res = None
    try:
        blast_res = NCBIWWW.qblast("blastn", "nt", valid_sequence)
    except:
        await ctx.send("An error ocurred while performing the BLAST.")
        return

    # read the BLAST search results and send the top 5 results as a threaded message
    try:
        record_iterator = SeqIO.parse(blast_res, "xml")
        top_results = []
        for i, record in enumerate(record_iterator):
            if i < 5:
                result = f"Sequence ID: {record.hit_id}\nDescription: {record.description}\nE-value: {record.hsps[0].expect}\n\n"
                top_results.append(result)
            else:
                break

        if top_results:
            response = "**Top 5 BLAST Results:**\n\n" + "\n".join(top_results)
            await ctx.reply(response, mention_author=True)
        else:
            await ctx.reply("BLAST search unsuccessful.")

    except:
        await ctx.send("An error occurred while processing the BLAST search.")
        return


bot.run(config("TOKEN"))
