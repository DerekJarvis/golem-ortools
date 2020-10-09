from yapapi.runner import Engine, Task, vm
from yapapi.runner.ctx import WorkContext
from datetime import timedelta
import asyncio


async def main():
    package = await vm.repo(
        image_hash="f3484f325c29f6dc3a858865738454889d5c2c476f501cb1d67db94f",
        min_mem_gib=1,
        min_storage_gib=2.0,
    )

    async def worker(ctx: WorkContext, tasks):
        ctx.send_file("./program.py", "/golem/work/program.py")
        async for task in tasks:
            ctx.begin()
            ctx.run("/golem/entrypoints/run.sh")
            ctx.download_file("/golem/output/results.txt", "results.txt")
            yield ctx.commit()
            # TODO: Check if job results are valid
            # and reject by: task.reject_task(msg = 'invalid file')
            task.accept_task()

        ctx.log("no more tasks!")

    
    # TODO make this dynamic, e.g. depending on the size of files to transfer
    # worst-case time overhead for initialization, e.g. negotiation, file transfer etc.
    # init_overhead: timedelta = timedelta(minutes=3)

    async with Engine(
        package=package,
        max_workers=1,
        budget=20.0,
        timeout=timedelta(minutes=10),
        subnet_tag="testnet",
    ) as engine:

        async for progress in engine.map(worker, [Task(data=0)]):
            print("progress=", progress)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    task = loop.create_task(main())
    try:
        asyncio.get_event_loop().run_until_complete(task)
    except (Exception, KeyboardInterrupt) as e:
        print(e)
        task.cancel()
        asyncio.get_event_loop().run_until_complete(asyncio.sleep(0.3))
