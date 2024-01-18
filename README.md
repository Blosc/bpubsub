![Figure: Caterva2 sequence diagram](./doc/_static/logo-caterva-small.png)

# Caterva2 - On demand access to remote Blosc2 data repositories

Caterva2 is a distributed system written in Python and meant for sharing Blosc2 datasets among different hosts by using a [publish–subscribe](https://en.wikipedia.org/wiki/Publish–subscribe_pattern) messaging pattern.  Here, publishers categorize datasets into root groups that are announced to the broker.  Also, every publisher exposes a REST interface that allows subscribers/clients to access the datasets.

Subscribers can access datasets on-demand and cache them locally. Additionally, cached data from a subscriber can be republished by another publisher. This is particularly useful for accessing remote datasets and sharing them within a local network, thereby optimizing communication and storage resources within work groups.


## Components of Caterva2

There are 4 elements:

- The broker. Enables communication between publishers and subscribers.
- The publisher(s). Makes datasets available to subscribers.
- The subscriber(s). Follows changes and allows the download of datasets from publishers.
- The client(s). A command line interface for the user to access the datasets, it connects
  to a subscriber.

These components have a number of requirements, which are all in the `pyproject.toml`
file, so just create a virtual environment and install:

```sh
pip install -e .[services,clients]
```

## Quick start

Start the broker:

```sh
cat2bro &
```

For the purpose of this quick start, let's use the datasets within the `root-example` folder:

```sh
ls -R root-example/
```

```
README.md         dir1/             dir2/             ds-1d.b2nd        ds-hello.b2frame

root-example//dir1:
ds-2d.b2nd  ds-3d.b2nd

root-example//dir2:
ds-4d.b2nd
```

Start publishing `root-example` datasets:

```sh
cat2pub foo root-example &
```

Now, let's create a subscriber:

```sh
cat2sub &
```

### The command line client

Now that we have the services running, we can start using a script (called `cat2cli`) that talks
to the subscriber. Now, in another shell, let's list all the available roots in the system:

```sh
cat2cli roots
```

```
foo
```

We only have a root called `foo` (the one we started publishing). If other publishers were running,
we would see them listed here too.

Let's ask our local subscriber to subscribe to the `foo` root:

```sh
cat2cli subscribe foo
```

Now, one can list the datasets in the `foo` root:

```sh
cat2cli list foo
```

```
foo/ds-hello.b2frame
foo/README.md
foo/ds-1d.b2nd
foo/dir2/ds-4d.b2nd
foo/dir1/ds-3d.b2nd
foo/dir1/ds-2d.b2nd
```

We can see how the client has subscribed successfully, and the datasets appear listed in the subscriptions.

Let's ask the subscriber more info about the `foo/dir2/ds-4d.b2nd` dataset:

```sh
cat2cli info foo/dir2/ds-4d.b2nd
```

```
{
    'dtype': 'complex128',
    'ndim': 4,
    'shape': [2, 3, 4, 5],
    'ext_shape': [2, 3, 4, 5],
    'chunks': [2, 3, 4, 5],
    'ext_chunks': [2, 3, 4, 5],
    'blocks': [2, 3, 4, 5],
    'blocksize': 1920,
    'chunksize': 1920,
    'schunk': {
        'blocksize': 1920,
        'cbytes': 0,
        'chunkshape': 120,
        'chunksize': 1920,
        'contiguous': True,
        'cparams': {'codec': 5, 'typesize': 16},
        'cratio': 0.0,
        'nbytes': 1920,
        'typesize': 16,
        'urlpath': '/Users/faltet/blosc/Caterva2/_caterva2/sub/cache/foo/dir2/ds-4d.b2nd',
        'nchunks': 1
    },
    'size': 1920
}
```

Also, we can ask for the url of a root:

```sh
cat2cli url foo
```

```
http://localhost:8001
```

Let's print data from a specified dataset:

```sh
cat2cli show foo/ds-hello.b2frame[:12]
```

```
Hello world!
```

It allows printing slices instead of the whole dataset too:

```sh
cat2cli show foo/dir2/ds-4d.b2nd[1,2,3]
```

```
[115.+115.j 116.+116.j 117.+117.j 118.+118.j 119.+119.j]
```

Finally, we can tell the subscriber to download the dataset:

```sh
cat2cli download foo/dir2/ds-4d.b2nd
```

```
Dataset saved to foo/dir2/ds-4d.b2nd
```

## Tools

Caterva2 includes a simple script to export the full group and dataset hierarchy in an HDF5 file to a new Caterva2 root directory.  You may invoke it like:

```sh
cat2import existing-hdf5-file.h5 new-caterva2-root
```

The tool is still pretty limited in its supported input and generated output, please invoke it with `--help` for more information.

## Tests

The tests can be run as follows:

```sh
pytest -v
```

In case you want to run the tests with existing running daemons (as we did above), you can do:

```shell
env CATERVA2_USE_EXTERNAL=1 pytest -v
```

Also, the tests suite comes with the package, so you can always run it as:

```sh
python -c "import caterva2 as cat2; cat2.test(verbose=True)"
```

The test publisher will use the files under `root-example`.  After tests finish, state files will be stored under `_caterva2_tests` in case you want to inspect them.


## Use with caution

Currently, this project is in early alpha stage, and it is not meant for production use yet.
In case you are interested in Caterva2, please contact us at contact@blosc.org.

That's all folks!
