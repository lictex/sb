import bpy
from . import utils

coco_colors = [
    ([220, 20, 60], ['person']),
    ([119, 11, 32], ['bicycle']),
    ([0, 0, 142], ['car']),
    ([0, 0, 230], ['motorcycle']),
    ([106, 0, 228], ['airplane']),
    ([0, 60, 100], ['bus']),
    ([0, 80, 100], ['train']),
    ([0, 0, 70], ['truck']),
    ([0, 0, 192], ['boat']),
    ([250, 170, 30], ['traffic light']),
    ([100, 170, 30], ['fire hydrant']),
    ([220, 220, 0], ['stop sign']),
    ([175, 116, 175], ['parking meter']),
    ([250, 0, 30], ['bench']),
    ([165, 42, 42], ['bird']),
    ([255, 77, 255], ['cat']),
    ([0, 226, 252], ['dog']),
    ([182, 182, 255], ['horse']),
    ([0, 82, 0], ['sheep']),
    ([120, 166, 157], ['cow']),
    ([110, 76, 0], ['elephant']),
    ([174, 57, 255], ['bear']),
    ([199, 100, 0], ['zebra']),
    ([72, 0, 118], ['giraffe']),
    ([255, 179, 240], ['backpack']),
    ([0, 125, 92], ['umbrella']),
    ([209, 0, 151], ['handbag']),
    ([188, 208, 182], ['tie']),
    ([0, 220, 176], ['suitcase']),
    ([255, 99, 164], ['frisbee']),
    ([92, 0, 73], ['skis']),
    ([133, 129, 255], ['snowboard']),
    ([78, 180, 255], ['sports ball']),
    ([0, 228, 0], ['kite']),
    ([174, 255, 243], ['baseball bat']),
    ([45, 89, 255], ['baseball glove']),
    ([134, 134, 103], ['skateboard']),
    ([145, 148, 174], ['surfboard']),
    ([255, 208, 186], ['tennis racket']),
    ([197, 226, 255], ['bottle']),
    ([171, 134, 1], ['wine glass']),
    ([109, 63, 54], ['cup']),
    ([207, 138, 255], ['fork']),
    ([151, 0, 95], ['knife']),
    ([9, 80, 61], ['spoon']),
    ([84, 105, 51], ['bowl']),
    ([74, 65, 105], ['banana']),
    ([166, 196, 102], ['apple']),
    ([208, 195, 210], ['sandwich']),
    ([255, 109, 65], ['orange']),
    ([0, 143, 149], ['broccoli']),
    ([179, 0, 194], ['carrot']),
    ([209, 99, 106], ['hot dog']),
    ([5, 121, 0], ['pizza']),
    ([227, 255, 205], ['donut']),
    ([147, 186, 208], ['cake']),
    ([153, 69, 1], ['chair']),
    ([3, 95, 161], ['couch']),
    ([163, 255, 0], ['potted plant']),
    ([119, 0, 170], ['bed']),
    ([0, 182, 199], ['dining table']),
    ([0, 165, 120], ['toilet']),
    ([183, 130, 88], ['tv']),
    ([95, 32, 0], ['laptop']),
    ([130, 114, 135], ['mouse']),
    ([110, 129, 133], ['remote']),
    ([166, 74, 118], ['keyboard']),
    ([219, 142, 185], ['cell phone']),
    ([79, 210, 114], ['microwave']),
    ([178, 90, 62], ['oven']),
    ([65, 70, 15], ['toaster']),
    ([127, 167, 115], ['sink']),
    ([59, 105, 106], ['refrigerator']),
    ([142, 108, 45], ['book']),
    ([196, 172, 0], ['clock']),
    ([95, 54, 80], ['vase']),
    ([128, 76, 255], ['scissors']),
    ([201, 57, 1], ['teddy bear']),
    ([246, 0, 122], ['hair drier']),
    ([191, 162, 208], ['toothbrush']),
    ([255, 255, 128], ['banner']),
    ([147, 211, 203], ['blanket']),
    ([150, 100, 100], ['bridge']),
    ([168, 171, 172], ['cardboard']),
    ([146, 112, 198], ['counter']),
    ([210, 170, 100], ['curtain']),
    ([92, 136, 89], ['door-stuff']),
    ([218, 88, 184], ['floor-wood']),
    ([241, 129, 0], ['flower']),
    ([217, 17, 255], ['fruit']),
    ([124, 74, 181], ['gravel']),
    ([70, 70, 70], ['house']),
    ([255, 228, 255], ['light']),
    ([154, 208, 0], ['mirror-stuff']),
    ([193, 0, 92], ['net']),
    ([76, 91, 113], ['pillow']),
    ([255, 180, 195], ['platform']),
    ([106, 154, 176], ['playingfield']),
    ([230, 150, 140], ['railroad']),
    ([60, 143, 255], ['river']),
    ([128, 64, 128], ['road']),
    ([92, 82, 55], ['roof']),
    ([254, 212, 124], ['sand']),
    ([73, 77, 174], ['sea']),
    ([255, 160, 98], ['shelf']),
    ([255, 255, 255], ['snow']),
    ([104, 84, 109], ['stairs']),
    ([169, 164, 131], ['tent']),
    ([225, 199, 255], ['towel']),
    ([137, 54, 74], ['wall-brick']),
    ([135, 158, 223], ['wall-stone']),
    ([7, 246, 231], ['wall-tile']),
    ([107, 255, 200], ['wall-wood']),
    ([58, 41, 149], ['water-other']),
    ([183, 121, 142], ['window-blind']),
    ([255, 73, 97], ['window-other']),
    ([107, 142, 35], ['tree-merged']),
    ([190, 153, 153], ['fence-merged']),
    ([146, 139, 141], ['ceiling-merged']),
    ([70, 130, 180], ['sky-other-merged']),
    ([134, 199, 156], ['cabinet-merged']),
    ([209, 226, 140], ['table-merged']),
    ([96, 36, 108], ['floor-other-merged']),
    ([96, 96, 96], ['pavement-merged']),
    ([64, 170, 64], ['mountain-merged']),
    ([152, 251, 152], ['grass-merged']),
    ([208, 229, 228], ['dirt-merged']),
    ([206, 186, 171], ['paper-merged']),
    ([152, 161, 64], ['food-other-merged']),
    ([116, 112, 0], ['building-other-merged']),
    ([0, 114, 143], ['rock-merged']),
    ([102, 102, 156], ['wall-other-merged']),
    ([250, 141, 255], ['rug-merged']),
]

ade20k_colors = [
    ([120, 120, 120], ["wall"]),
    ([180, 120, 120], ["building", "edifice"]),
    ([6, 230, 230], ["sky"]),
    ([80, 50, 50], ["floor", "flooring"]),
    ([4, 200, 3], ["tree"]),
    ([120, 120, 80], ["ceiling"]),
    ([140, 140, 140], ["road", "route"]),
    ([204, 5, 255], ["bed"]),
    ([230, 230, 230], ["windowpane", "window"]),
    ([4, 250, 7], ["grass"]),
    ([224, 5, 255], ["cabinet"]),
    ([235, 255, 7], ["sidewalk", "pavement"]),
    ([150, 5, 61], ["person", "individual",
                    "someone", "somebody", "mortal", "soul"]),
    ([120, 120, 70], ["earth", "ground"]),
    ([8, 255, 51], ["door", "double", "door"]),
    ([255, 6, 82], ["table"]),
    ([143, 255, 140], ["mountain", "mount"]),
    ([204, 255, 4], ["plant", "flora", "plant", "life"]),
    ([255, 51, 7], ["curtain", "drape", "drapery", "mantle", "pall"]),
    ([204, 70, 3], ["chair"]),
    ([0, 102, 200], ["car", "auto", "automobile", "machine", "motorcar"]),
    ([61, 230, 250], ["water"]),
    ([255, 6, 51], ["painting", "picture"]),
    ([11, 102, 255], ["sofa", "couch", "lounge"]),
    ([255, 7, 71], ["shelf"]),
    ([255, 9, 224], ["house"]),
    ([9, 7, 230], ["sea"]),
    ([220, 220, 220], ["mirror"]),
    ([255, 9, 92], ["rug", "carpet", "carpeting"]),
    ([112, 9, 255], ["field"]),
    ([8, 255, 214], ["armchair"]),
    ([7, 255, 224], ["seat"]),
    ([255, 184, 6], ["fence", "fencing"]),
    ([10, 255, 71], ["desk"]),
    ([255, 41, 10], ["rock", "stone"]),
    ([7, 255, 255], ["wardrobe", "closet", "press"]),
    ([224, 255, 8], ["lamp"]),
    ([102, 8, 255], ["bathtub", "bathing", "tub", "bath", "tub"]),
    ([255, 61, 6], ["railing", "rail"]),
    ([255, 194, 7], ["cushion"]),
    ([255, 122, 8], ["base", "pedestal", "stand"]),
    ([0, 255, 20], ["box"]),
    ([255, 8, 41], ["column", "pillar"]),
    ([255, 5, 153], ["signboard", "sign"]),
    ([6, 51, 255], ["chest", "of", "drawers", "chest", "bureau", "dresser"]),
    ([235, 12, 255], ["counter"]),
    ([160, 150, 20], ["sand"]),
    ([0, 163, 255], ["sink"]),
    ([140, 140, 140], ["skyscraper"]),
    ([250, 10, 15], ["fireplace", "hearth", "open", "fireplace"]),
    ([20, 255, 0], ["refrigerator", "icebox"]),
    ([31, 255, 0], ["grandstand", "covered", "stand"]),
    ([255, 31, 0], ["path"]),
    ([255, 224, 0], ["stairs", "steps"]),
    ([153, 255, 0], ["runway"]),
    ([0, 0, 255], ["case", "display", "case", "showcase", "vitrine"]),
    ([255, 71, 0], ["pool", "table", "billiard", "table", "snooker", "table"]),
    ([0, 235, 255], ["pillow"]),
    ([0, 173, 255], ["screen", "door", "screen"]),
    ([31, 0, 255], ["stairway", "staircase"]),
    ([11, 200, 200], ["river"]),
    ([255, 82, 0], ["bridge", "span"]),
    ([0, 255, 245], ["bookcase"]),
    ([0, 61, 255], ["blind", "screen"]),
    ([0, 255, 112], ["coffee", "table", "cocktail", "table"]),
    ([0, 255, 133], ["toilet", "can", "commode",
                     "crapper", "pot", "potty", "stool", "throne"]),
    ([255, 0, 0], ["flower"]),
    ([255, 163, 0], ["book"]),
    ([255, 102, 0], ["hill"]),
    ([194, 255, 0], ["bench"]),
    ([0, 143, 255], ["countertop"]),
    ([51, 255, 0], ["stove", "kitchen", "stove",
                    "range", "kitchen", "range", "cooking", "stove"]),
    ([0, 82, 255], ["palm", "palm", "tree"]),
    ([0, 255, 41], ["kitchen", "island"]),
    ([0, 255, 173], ["computer", "computing", "machine", "computing", "device", "data",
                     "processor", "electronic", "computer", "information", "processing", "system"]),
    ([10, 0, 255], ["swivel", "chair"]),
    ([173, 255, 0], ["boat"]),
    ([0, 255, 153], ["bar"]),
    ([255, 92, 0], ["arcade", "machine"]),
    ([255, 0, 255], ["hovel", "hut", "hutch", "shack", "shanty"]),
    ([255, 0, 245], ["bus", "autobus", "coach", "charabanc", "double-decker",
                     "jitney", "motorbus", "motorcoach", "omnibus", "passenger", "vehicle"]),
    ([255, 0, 102], ["towel"]),
    ([255, 173, 0], ["light", "light", "source"]),
    ([255, 0, 20], ["truck", "motortruck"]),
    ([255, 184, 184], ["tower"]),
    ([0, 31, 255], ["chandelier", "pendant", "pendent"]),
    ([0, 255, 61], ["awning", "sunshade", "sunblind"]),
    ([0, 71, 255], ["streetlight", "street", "lamp"]),
    ([255, 0, 204], ["booth", "cubicle", "stall", "kiosk"]),
    ([0, 255, 194], ["television", "television", "receiver", "television", "set",
                     "tv", "tv", "set", "idiot", "box", "boob", "tube", "telly", "goggle", "box"]),
    ([0, 255, 82], ["airplane", "aeroplane", "plane"]),
    ([0, 10, 255], ["dirt", "track"]),
    ([0, 112, 255], ["apparel", "wearing", "apparel", "dress", "clothes"]),
    ([51, 0, 255], ["pole"]),
    ([0, 194, 255], ["land", "ground", "soil"]),
    ([0, 122, 255], ["bannister", "banister",
                     "balustrade", "balusters", "handrail"]),
    ([0, 255, 163], ["escalator", "moving",
                     "staircase", "moving", "stairway"]),
    ([255, 153, 0], ["ottoman", "pouf", "pouffe", "puff", "hassock"]),
    ([0, 255, 10], ["bottle"]),
    ([255, 112, 0], ["buffet", "counter", "sideboard"]),
    ([143, 255, 0], ["poster", "posting",
                     "placard", "notice", "bill", "card"]),
    ([82, 0, 255], ["stage"]),
    ([163, 255, 0], ["van"]),
    ([255, 235, 0], ["ship"]),
    ([8, 184, 170], ["fountain"]),
    ([133, 0, 255], ["conveyer", "belt", "conveyor",
                     "belt", "conveyer", "conveyor", "transporter"]),
    ([0, 255, 92], ["canopy"]),
    ([184, 0, 255], ["washer", "automatic", "washer", "washing", "machine"]),
    ([255, 0, 31], ["plaything", "toy"]),
    ([0, 184, 255], ["swimming", "pool", "swimming", "bath", "natatorium"]),
    ([0, 214, 255], ["stool"]),
    ([255, 0, 112], ["barrel", "cask"]),
    ([92, 255, 0], ["basket", "handbasket"]),
    ([0, 224, 255], ["waterfall", "falls"]),
    ([112, 224, 255], ["tent", "collapsible", "shelter"]),
    ([70, 184, 160], ["bag"]),
    ([163, 0, 255], ["minibike", "motorbike"]),
    ([153, 0, 255], ["cradle"]),
    ([71, 255, 0], ["oven"]),
    ([255, 0, 163], ["ball"]),
    ([255, 204, 0], ["food", "solid", "food"]),
    ([255, 0, 143], ["step", "stair"]),
    ([0, 255, 235], ["tank", "storage", "tank"]),
    ([133, 255, 0], ["trade", "name", "brand", "name", "brand", "marque"]),
    ([255, 0, 235], ["microwave", "microwave", "oven"]),
    ([245, 0, 255], ["pot", "flowerpot"]),
    ([255, 0, 122], ["animal", "animate", "being",
                     "beast", "brute", "creature", "fauna"]),
    ([255, 245, 0], ["bicycle", "bike", "wheel", "cycle"]),
    ([10, 190, 212], ["lake"]),
    ([214, 255, 0], ["dishwasher", "dish",
                     "washer", "dishwashing", "machine"]),
    ([0, 204, 255], ["screen", "silver", "screen", "projection", "screen"]),
    ([20, 0, 255], ["blanket", "cover"]),
    ([255, 255, 0], ["sculpture"]),
    ([0, 153, 255], ["hood", "exhaust", "hood"]),
    ([0, 41, 255], ["sconce"]),
    ([0, 255, 204], ["vase"]),
    ([41, 0, 255], ["traffic", "light", "traffic", "signal", "stoplight"]),
    ([41, 255, 0], ["tray"]),
    ([173, 0, 255], ["ashcan", "trash", "can", "garbage", "can", "wastebin", "ash",
                     "bin", "ash-bin", "ashbin", "dustbin", "trash", "barrel", "trash", "bin"]),
    ([0, 245, 255], ["fan"]),
    ([71, 0, 255], ["pier", "wharf", "wharfage", "dock"]),
    ([122, 0, 255], ["crt", "screen"]),
    ([0, 255, 184], ["plate"]),
    ([0, 92, 255], ["monitor", "monitoring", "device"]),
    ([184, 255, 0], ["bulletin", "board", "notice", "board"]),
    ([0, 133, 255], ["shower"]),
    ([255, 214, 0], ["radiator"]),
    ([25, 194, 194], ["glass", "drinking", "glass"]),
    ([102, 255, 0], ["clock"]),
    ([92, 0, 255], ["flag"]),
]


def def_seg(seg_list, name):
    items = bpy.props.EnumProperty(items=tuple([
        (
            str(i),
            "; ".join(s),
            f"RGB: {', '.join(str(c) for c in c)}"
        )
        for i, (c, s) in enumerate(seg_list)
    ]))

    class SegColorSearchPopup(utils.NodeOperator):
        bl_idname = f"sd.search_seg_color_{name.lower()}"
        bl_label = "Search"
        bl_property = "seg_id"
        bl_options = {'REGISTER', 'UNDO'}

        seg_id: items

        def execute(self, context):
            self.node.seg_id = self.seg_id
            self.node.update()
            bpy.context.region.tag_redraw()
            return {'FINISHED'}

        def invoke(self, context, event):
            wm = context.window_manager
            wm.invoke_search_popup(self)
            return {'FINISHED'}

    class ShaderNodeSeg(utils.CustomShaderNode):
        bl_idname = f'ShaderNodeSDSeg{name}'
        bl_label = f'{name} Color'

        seg_id: items

        def update(self):
            id = int(self.seg_id)
            try:
                self.node_tree.nodes["Group Output"].inputs['Color'].default_value = [
                    *[x/255 for x in seg_list[id][0]], 1.0
                ]
            except:
                pass

        def draw_buttons(self, context, layout):
            layout.label(text=", ".join(seg_list[int(self.seg_id)][1]))
            SegColorSearchPopup.ui(self, layout)

        def init_node_tree(self, **k):
            super().init_node_tree(
                inputs=[],
                outputs=[
                    ('NodeSocketColor', "Color")
                ],
                **k,
            )

            self.node_tree.nodes.new("NodeGroupOutput")

    return ShaderNodeSeg, [ShaderNodeSeg, SegColorSearchPopup]


ShaderNodeSegADE20K, classes_ADE20K = def_seg(ade20k_colors, "ADE20K")
ShaderNodeSegCOCO, classes_COCO = def_seg(coco_colors, "COCO")


class CompositorNodeSeg(utils.CustomCompositorNode):
    bl_idname = 'CompositorNodeSDSeg'
    bl_label = 'Segmentation Postprocess'

    def init_node_tree(self, **k):
        super().init_node_tree(
            inputs=[
                ('NodeSocketColor', "AOV Output")
            ],
            outputs=[
                ('NodeSocketColor', "Color")
            ],
            **k,
        )

        input = self.node_tree.nodes.new("NodeGroupInput")
        blend = self.node_tree.nodes.new("CompositorNodeAlphaOver")
        blend.inputs[1].default_value = [0.0, 0.0, 0.0, 1.0]
        output = self.node_tree.nodes.new("NodeGroupOutput")

        self.node_tree.links.new(
            input.outputs["AOV Output"],
            blend.inputs[2],
        )
        self.node_tree.links.new(
            blend.outputs[0],
            output.inputs["Color"],
        )


classes = [
    *classes_ADE20K,
    *classes_COCO,
    CompositorNodeSeg
]

nodes = [
    ("SHADER", ShaderNodeSegADE20K),
    ("SHADER", ShaderNodeSegCOCO),
    ("COMPOSITOR", CompositorNodeSeg),
]
